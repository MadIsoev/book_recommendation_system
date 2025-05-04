import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="NextBook — рекомендательная система",
    page_icon="📚",
    layout="wide"
)

# Подключаем шрифты Google Fonts
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Roboto&display=swap" rel="stylesheet">
    <style>
    body {
        font-family: 'Roboto', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif;
    }
    .stButton>button {
        font-family: 'Roboto', sans-serif;
    }
    .recommendation-card h3 {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(""" 
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white; /* Button text color */
    }
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin: 1rem 0;
        border-left: 5px solid #FF4B4B;
        color : black;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color:black;
    }
    h1 {
        color: #FF4B4B;
    }
    h3, h2, h4 {
        color: black;
    }
    h6 {
        color: black;
    }

    /* Style for the subtitle */
    .subtitle {
        color: white; /* Change subtitle color to white */
        font-size: 16px;
        background-color: #FF4B4B;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

class BookRecommender:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.df['title'] = self.df['title'].str.strip()
        self.df['authors'] = self.df['authors'].str.strip()
        self.df['clean_title'] = self.df['title'].str.replace(r'\(.*\)', '').str.strip()
        
        self.df['publication_date'] = pd.to_datetime(self.df['publication_date'], errors='coerce')
        self.df = self.df.dropna(subset=['title', 'authors', 'average_rating'])

    def get_title_similarity(self, title1, title2):
        return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    
    def get_author_similarity(self, author1, author2):
        authors1 = set(author1.lower().replace('/', ',').split(','))
        authors2 = set(author2.lower().replace('/', ',').split(','))
        intersection = len(authors1.intersection(authors2))
        union = len(authors1.union(authors2))
        return intersection / union if union > 0 else 0

    def recommend_books(self, query, by='title', n_recommendations=5):
        similarities = []
        
        if by == 'title':
            for idx, row in self.df.iterrows():
                similarity = self.get_title_similarity(query, row['clean_title'])
                if similarity < 1.0:  
                    similarities.append(self._create_recommendation_dict(row, similarity))
        
        elif by == 'author':
            for idx, row in self.df.iterrows():
                similarity = self.get_author_similarity(query, row['authors'])
                similarities.append(self._create_recommendation_dict(row, similarity))
        
        return sorted(similarities, 
                     key=lambda x: (x['similarity'], x['average_rating']), 
                     reverse=True)[:n_recommendations]
    
    def _create_recommendation_dict(self, row, similarity):
        recommendation = {
            'bookID': row['bookID'],
            'title': row['title'],
            'authors': row['authors'],
            'similarity': similarity,
            'average_rating': row['average_rating'],
            'publication_date': row['publication_date'],
            'ratings_count': row['ratings_count']
        }
        
        recommendation['num_pages'] = row['num_pages'] if 'num_pages' in row else 'N/A'  
        
        return recommendation
 
@st.cache_data
def load_data():
    try: 
        data = pd.read_csv("books.csv", on_bad_lines='skip')   
        # Clean the data
        data['title'] = data['title'].str.strip()  
        data['authors'] = data['authors'].str.strip()  
        data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
        data = data.dropna(subset=['title', 'authors', 'average_rating'])  
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def main():
    st.title("📚 NextBook — найди свою следующую любимую книгу")
    st.markdown("#### Открой мир новых любимых книг!")
 
    data = load_data()
    
    if data.empty:
        st.error("No data available to display. Please check the CSV file.")
        return

    recommender = BookRecommender(data)
 
    st.sidebar.header("Recommendation Settings")
 
    search_type = st.sidebar.radio(
        "Search by:",
        ["Book Title", "Author"],
        key="search_type"
    )
 
    if search_type == "Book Title":
        query = st.sidebar.selectbox(
            "Select a book:",
            options=data['title'].unique(),
            key="book_dropdown"
        )
        by = 'title'
    else:
        query = st.sidebar.selectbox(
            "Select an author:",
            options=data['authors'].unique(),
            key="author_dropdown"
        )
        by = 'author'

    n_recommendations = st.sidebar.slider(
        "Number of recommendations:",
        min_value=1,
        max_value=10,
        value=5
    )
 
    if st.sidebar.button("Get Recommendations"):
        recommendations = recommender.recommend_books(query, by, n_recommendations)
         
        for i, book in enumerate(recommendations, 1):
            with st.container():
                st.markdown(f"""
                <div class="recommendation-card">
                    <h3>{i}. {book['title']}</h3>
                    <p><strong>Author(s):</strong> {book['authors']}</p>
                    <p><strong>Similarity Score:</strong> {book['similarity']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
 
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" 
                        viewBox="0 0 24 24" fill="none" stroke="#FF9900" stroke-width="2" 
                        stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 
                        18.18 21.02 12 17.77 5.82 21.02 
                        7 14.14 2 9.27 8.91 8.26 12 2" /></svg> Rating</h4>
                        <h2>{book['average_rating']:.2f}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" 
                        viewBox="0 0 24 24" fill="none" stroke="#0077cc" stroke-width="2" 
                        stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                        <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v15H6.5A2.5 
                        2.5 0 0 1 4 14.5z" /></svg> Pages</h4>
                        <h2>{book['num_pages']}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" 
                        viewBox="0 0 24 24" fill="none" stroke="#28a745" stroke-width="2" 
                        stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 
                        2-2h11a2 2 0 0 1 2 2z"/></svg> Reviews</h4>
                        <h2>{book['ratings_count']:,}</h2>
                    </div>
                    """, unsafe_allow_html=True)
 
        st.subheader("📊 Visualization")
 
        fig_ratings = px.bar(
            pd.DataFrame(recommendations),
            x='title',
            y='average_rating',
            title='Ratings Comparison',
            labels={'title': 'Book Title', 'average_rating': 'Average Rating'},
            color='average_rating',
            color_continuous_scale='reds'
        )
        fig_ratings.update_layout(showlegend=False)
        st.plotly_chart(fig_ratings, use_container_width=True)

if __name__ == "__main__":
    main()

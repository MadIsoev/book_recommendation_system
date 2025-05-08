import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import plotly.express as px
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

st.set_page_config(
    page_title="NextBook — рекомендательная система",
    page_icon="📚",
    layout="wide"
)

# Новый стиль
style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Open+Sans:wght@400;600&display=swap');

        .main {
            padding: 2rem;
            font-family: 'Open Sans', sans-serif;
        }
        h1, h2, h3, h4, h5 {
            font-family: 'Roboto', sans-serif;
            color: #4A4A4A;
        }

        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg, #6C63FF, #A084DC);
            color: white;
            border: none;
            padding: 0.6rem;
            border-radius: 0.5rem;
            font-weight: bold;
            transition: background 0.3s ease, transform 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #4C47E3, #6F5BB5);
            transform: scale(1.05);
            color: white;
        }
        .recommendation-card {
            padding: 1.5rem;
            border-radius: 1rem;
            background: linear-gradient(135deg, #F0F0F5, #D9D9E4);
            margin: 1rem 0;
            border-left: 5px solid #6C63FF;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            color: #333333;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .recommendation-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        }
        .metric-card {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.8rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: black;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        </style>
    """, unsafe_allow_html=True)

class BookRecommender:
    def __init__(self, data):
        self.df = pd.DataFrame(data)
        self.df['title'] = self.df['title'].str.strip()
        self.df['authors'] = self.df['authors'].str.strip()
        self.df['clean_title'] = self.df['title'].str.replace(r'\(.*\)', '', regex=True).str.strip()
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

        return sorted(similarities, key=lambda x: (x['similarity'], x['average_rating']), reverse=True)[:n_recommendations]

    def _create_recommendation_dict(self, row, similarity):
        return {
            'bookID': row['bookID'],
            'title': row['title'],
            'authors': row['authors'],
            'similarity': similarity,
            'average_rating': row['average_rating'],
            'publication_date': row.get('publication_date', 'N/A'),
            'ratings_count': row.get('ratings_count', 0),
            'num_pages': row.get('num_pages', 'N/A')
        }


@st.cache_data
def load_data():
    try:
        data = pd.read_csv("books.csv", on_bad_lines='skip')
        data['title'] = data['title'].str.strip()
        data['authors'] = data['authors'].str.strip()
        data['publication_date'] = pd.to_datetime(data['publication_date'], errors='coerce')
        data = data.dropna(subset=['title', 'authors', 'average_rating'])
        return data
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()


def main():
    st.title("📚 NextBook — найди свою следующую любимую книгу")
    st.markdown("""
    **NextBook** — это интеллектуальная рекомендательная система, которая помогает пользователю найти новую интересную книгу на основе:
    - Названия книги 📖
    - Имени автора 👩‍💼  
    """)
    st.markdown("#### Открой мир новых любимых книг!")
    
    data = load_data()
    if data.empty:
        st.error("Данные не загружены. Проверь файл CSV.")
        return

    recommender = BookRecommender(data)

    st.sidebar.header("Настройки рекомендаций")

    search_type = st.sidebar.radio(
        "Искать по:",
        ["Название книги", "Автор"]
    )

    if search_type == "Название книги":
        query = st.sidebar.selectbox("Выберите книгу:", options=data['title'].unique())
        by = 'title'
    else:
        query = st.sidebar.selectbox("Выберите автора:", options=data['authors'].unique())
        by = 'author'

    n_recommendations = st.sidebar.slider(
        "Количество рекомендаций:",
        min_value=1,
        max_value=10,
        value=5
    )

    if st.sidebar.button("Получить рекомендации"):
        recommendations = recommender.recommend_books(query, by, n_recommendations)

        tab1, tab2 = st.tabs(["📖 Рекомендации", "📊 Аналитика"])

        with tab1:
            for i, book in enumerate(recommendations, 1):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3>{i}. {book['title']}</h3>
                        <p><strong>Автор(ы):</strong> {book['authors']}</p>
                        <p><strong>Похожесть:</strong> {book['similarity']:.2f}</p>
                        <p><strong>Дата публикации:</strong> {book['publication_date'].date() if pd.notnull(book['publication_date']) else 'Неизвестно'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Рейтинг</h4>
                            <h2>⭐ {book['average_rating']:.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Страниц</h4>
                            <h2>📄 {book['num_pages']}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>Оценок</h4>
                            <h2>📊 {book['ratings_count']:,}</h2>
                        </div>
                        """, unsafe_allow_html=True)

        with tab2: # График баров: средние рейтинги рекомендованных книг
            fig_ratings = px.bar(
                pd.DataFrame(recommendations),
                x='title',
                y='average_rating',
                title='Сравнение рейтингов книг',
                labels={'title': 'Название книги', 'average_rating': 'Средний рейтинг'},
                color='average_rating',
                color_continuous_scale='purples'
            )
            fig_ratings.update_layout(showlegend=False)
            st.plotly_chart(fig_ratings, use_container_width=True)
            
            # Дополнительные графики — на основе всего датасета
            st.markdown("### 📈 Топ-10 самых популярных книг")
            
            # Топ-10 популярных книг
            book_counts = (
                data.groupby('title')['average_rating']
                .count()
                .sort_values(ascending=False)
            )
            popular_books = book_counts.reset_index()
            popular_books.columns = ['title', 'rating_count']
            
            top_10_books = popular_books.head(10)
            
            # Построение графика через matplotlib/seaborn
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='rating_count', y='title', data=top_10_books, palette='Set3', ax=ax)
            ax.set_xlabel('Рейтинг', fontsize=12)
            ax.set_ylabel('Название книги', fontsize=12)
            ax.set_title('Топ-10 самых популярных книг по рейтингу', fontsize=14)
            st.pyplot(fig)
            
            # Облако слов — названия книг по рейтингу
            st.subheader("☁️ Облако популярных книг")
            book_string = " ".join((title + " ") * count for title, count in book_counts.items())
            
            custom_stopwords = set(STOPWORDS) - {"the", "a", "and", "in", "is", "of", "to"}
            
            wc = WordCloud(
                width=1000,
                height=600,
                max_font_size=120,
                stopwords=custom_stopwords,
                background_color='white'
            ).generate(book_string)
            
            fig_wc, ax_wc = plt.subplots(figsize=(16, 8))
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis('off')

            st.pyplot(fig_wc)

            st.markdown("---")
            
            st.subheader("📚 Топ-10 авторов")
            
            # Подсчёт количества оценок по авторам
            author_counts = (
                data.groupby('authors')['average_rating']
                .count()
                .sort_values(ascending=False)
            )
            
            top_authors = author_counts.head(10).reset_index()
            top_authors.columns = ['authors', 'rating_count']
            
            # Построение графика Seaborn
            fig_authors, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='rating_count', y='authors', data=top_authors, palette='viridis', ax=ax)
            ax.set_xlabel('Количество оценок', fontsize=12)
            ax.set_ylabel('Автор', fontsize=12)
            ax.set_title('Топ-10 авторов по количеству оценок', fontsize=16)
            st.pyplot(fig_authors)
            
            # Облако слов по авторам
            st.subheader("☁️ Облако популярных авторов")
            
            author_string = " ".join((author + " ") * count for author, count in author_counts.items())
            
            stop_words = set(STOPWORDS)
            
            wc = WordCloud(
                width=1000,
                height=600,
                max_font_size=120,
                stopwords=stop_words,
                background_color='white'
            ).generate(author_string)
            
            fig_wc, ax_wc = plt.subplots(figsize=(12, 6))
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis('off')
            st.pyplot(fig_wc)


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import plotly.express as px
from datetime import datetime

import streamlit as st

import streamlit as st

# Устанавливаем начальную страницу
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Стилизация кнопок во вкладки ---
st.markdown("""
    <style>
    .sidebar-tab button {
        width: 100%;
        margin-bottom: 5px;
        padding: 0.5rem 1rem;
        border: none;
        background: #f0f0f5;
        color: #333;
        font-weight: 600;
        border-radius: 10px;
        text-align: left;
        transition: 0.2s ease-in-out;
    }
    .sidebar-tab button:hover {
        background: #d6d6f5;
        color: #000;
    }
    .sidebar-tab button.active {
        background: #6C63FF;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Боковая панель как вкладки ---
with st.sidebar:
    st.markdown("### 📘 Меню")
    st.markdown('<div class="sidebar-tab">', unsafe_allow_html=True)
    
    if st.button("🏠 Главная", key="home_btn"):
        st.session_state.page = "home"
    if st.button("📚 Рекомендации", key="rec_btn"):
        st.session_state.page = "recommend"
    if st.button("📊 Аналитика", key="analytics_btn"):
        st.session_state.page = "analytics"
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Отображение страниц ---
if st.session_state.page == "home":
    st.title("🏠 Главная")
    st.write("Добро пожаловать!")

elif st.session_state.page == "recommend":
    st.set_page_config(
    page_title="NextBook — сервис рекомендаций книг",
    page_icon="📚",
    layout="wide"
    )

st.markdown("""
    <style>
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
    .stButton>button:active {
        background: linear-gradient(90deg, #8A7DFF, #7D6BFF) !important;
        color: white !important;
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

    .subtitle {
        color: white;
        font-size: 16px;
        background-color: #6C63FF;
        padding: 10px;
        border-radius: 5px;
    }

    .stSelectbox select {
        font-family: 'Open Sans', sans-serif;
        font-size: 14px;
    }

    [data-testid="column"] {
        background-color: #f9f9f9 !important;
        padding: 1rem;
        border-radius: 10px;
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

        tab1, tab2 = st.tabs(["📖 Рекомендации", "📊 График оценок"])

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

        with tab2:
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


if __name__ == "__main__":
    main()

elif st.session_state.page == "analytics":
    st.title("📊 Аналитика")
    st.write("Здесь графики и анализ.")







# Импорт библиотек
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import plotly.express as px
from datetime import datetime

# Конфигурация страницы
st.set_page_config(
    page_title="NextBook — рекомендательная система",
    page_icon="📚",
    layout="wide"
)

# Пользовательские стили
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        transition: 0.3s ease-in-out;
    }
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background-color: #f0f4f8;
        margin: 1rem 0;
        border-left: 6px solid #4A90E2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }
    h1 {
        color: #4A90E2;
    }
    h2, h3, h4, h6 {
        color: #111111;
    }
    .subtitle {
        color: white;
        font-size: 16px;
        background-color: #4A90E2;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Класс рекомендательной системы
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
        for idx, row in self.df.iterrows():
            if by == 'title':
                similarity = self.get_title_similarity(query, row['clean_title'])
                if similarity < 1.0:
                    similarities.append(self._create_recommendation_dict(row, similarity))
            else:
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
            'publication_date': row['publication_date'],
            'ratings_count': row['ratings_count'],
            'num_pages': row['num_pages'] if pd.notnull(row.get('num_pages')) else 'N/A'
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
        st.error(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()

# Основная функция
def main():
    st.title("📚 NextBook — найди свою следующую любимую книгу")
    st.markdown("#### Открой мир новых любимых книг!")

    data = load_data()
    if data.empty:
        st.error("Данные не загружены. Проверь CSV-файл.")
        return

    recommender = BookRecommender(data)

    st.sidebar.header("Параметры рекомендации")
    search_type = st.sidebar.radio("Поиск по:", ["Название книги", "Автор"])

    if search_type == "Название книги":
        query = st.sidebar.selectbox("Выберите книгу:", options=data['title'].unique())
        by = 'title'
    else:
        query = st.sidebar.selectbox("Выберите автора:", options=data['authors'].unique())
        by = 'author'

    n_recommendations = st.sidebar.slider("Количество рекомендаций:", 1, 10, 5)

    if st.sidebar.button("🔍 Получить рекомендации"):
        recommendations = recommender.recommend_books(query, by, n_recommendations)

        for i, book in enumerate(recommendations, 1):
            with st.container():
                st.markdown(f"""
                <div class="recommendation-card">
                    <h3>{i}. {book['title']}</h3>
                    <p><strong>Автор(ы):</strong> {book['authors']}</p>
                    <p><strong>Сходство:</strong> {book['similarity']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Рейтинг</h4>
                        <h2>🌟 {book['average_rating']:.2f}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Страниц</h4>
                        <h2>📘 {book['num_pages']}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Оценок</h4>
                        <h2>💬 {book['ratings_count']:,}</h2>
                    </div>
                    """, unsafe_allow_html=True)

        st.subheader("📊 График оценок")
        fig_ratings = px.bar(
            pd.DataFrame(recommendations),
            x='title',
            y='average_rating',
            title='Сравнение рейтингов',
            labels={'title': 'Книга', 'average_rating': 'Рейтинг'},
            color='average_rating',
            color_continuous_scale='Blues'
        )
        fig_ratings.update_layout(showlegend=False)
        st.plotly_chart(fig_ratings, use_container_width=True)

if __name__ == "__main__":
    main()

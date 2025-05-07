# 📚 Проект: Books Recommendation System

**Цель проекта:**
Создать рекомендательную систему для книг, которая поможет пользователям находить интересные произведения на основе их предпочтений и информации о книгах. Система должна использовать как коллаборативную фильтрацию, так и контентные характеристики книг.

Этот проект строит рекомендательную систему книг на основе трех датасетов: Users, Ratings и Books.

**Что сделано:**
- Загрузка и подготовка данных.
- Анализ данных (**EDA**).
- Подготовка выборок.
- Подготовка и обучение модели (**KNN** на косинусной метрике, **SVD** и **Cosine Similarity**).
- Реализация функции получения рекомендаций:
    - по названию книги (item-based)
    - по пользователю (user-based)
    - по автору.
- Оценка качества модели с использованием метрик **Precision, Recall, MAP, MRR.**

**Использованные библиотеки:** pandas, numpy, sklearn, scipy, matplotlib и seaborn.


## App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nextbook.streamlit.app/)

## GitHub Codespaces

[![Open in GitHub Codespaces](https://[github.com/codespaces/badge.svg](https://github.com/MadIsoev/book_recommendation_system))]


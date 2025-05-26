import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("KINOPOISK_API_KEY")

class KinopoiskAPI:
    BASE_URL = "https://api.kinopoisk.dev/v1.4"

    @staticmethod
    def search_movies(query: str, limit: int = 5) -> List[Dict]:
        headers = {
            "accept": "application/json",
            "X-API-KEY": API_KEY,
        }
        params = {
            "query": query,
            "limit": limit,
        }
        try:
            response = requests.get(f"{KinopoiskAPI.BASE_URL}/movie/search", headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("docs", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return []

    @staticmethod
    def get_popular_movies(limit: int = 5) -> List[Dict]:
        headers = {
            "accept": "application/json",
            "X-API-KEY": API_KEY,
        }
        params = {
            "limit": limit,
            "sortField": "votes.kp",
            "sortType": "-1",
            "type": "movie",
        }
        try:
            response = requests.get(f"{KinopoiskAPI.BASE_URL}/movie", headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("docs", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса популярных фильмов: {e}")
            return []

    @staticmethod
    def get_popular_series(limit: int = 5) -> List[Dict]:
        headers = {
            "accept": "application/json",
            "X-API-KEY": API_KEY,
        }
        params = {
            "limit": limit,
            "sortField": "votes.kp",
            "sortType": "-1",
            "type": "tv-series",
        }
        try:
            response = requests.get(f"{KinopoiskAPI.BASE_URL}/movie", headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("docs", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса популярных сериалов: {e}")
            return []

    @staticmethod
    def format_movie_info(movie: Dict) -> str:
        name = movie.get("name", "Нет данных")
        year = movie.get("year", "Нет данных")
        rating = movie.get("rating", {}).get("kp", "Нет данных")
        description = movie.get("description", "Нет описания")
        description = description[:300] + "..." if description else "Нет описания"
        movie_url = f"https://www.kinopoisk.ru/film/{movie.get('id', '')}/"

        return (
            f"🎬 <b>{name}</b> ({year})\n"
            f"⭐ <b>Рейтинг:</b> {rating}\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"🔗 <a href='{movie_url}'>Ссылка на Кинопоиск</a>\n"
            f"{'═' * 30}"
        )

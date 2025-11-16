# Автоматизированное тестирование API микросервиса объявлений

Данный репозиторий содержит автоматизированные тесты для проверки API микросервиса объявлений.

## Описание проекта

API микросервиса объявлений имеет 4 основных эндпоинта:
1. Создание объявления (POST /ads)
2. Получение объявления по ID (GET /ads/{id})
3. Получение всех объявлений по ID продавца (GET /ads/sellers/{sellerId})
4. Получение статистики по item ID (GET /stats/{itemId})

## Требования

- Python 3.8 или новее
- Библиотеки: pytest, requests

## Установка

1. Создать виртуальное окружение

python -m venv venv
venv\Scripts\activate

2. Запуск тестов
Запуск всех тестов
pytest tests/test_ads_api.py -v

Запуск конкретного класса тестов:
pytest tests/test_ads_api.py::TestCreateAd -v

Запуск конкретного тест-кейса:
pytest tests/test_ads_api.py::TestCreateAd::test_create_ad_with_valid_data -v

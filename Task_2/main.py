import pytest
import requests
import random
import time
from datetime import datetime


URL = "https://qa-internship.avito.com"

def generate_seller_id():
    return random.randint(111111, 999999)

def generate_ad_data(seller_id=None):
    if seller_id is None:
        seller_id = generate_seller_id()
    
    current_timestamp = int(time.time())
    
    return {
        "title": f"Test Ad {current_timestamp}",
        "description": f"This is an automated test ad created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "price": random.randint(100, 10000),
        "sellerId": seller_id,
        "itemId": random.randint(1000000, 9999999)
    }

@pytest.fixture
def create_ad():
    ad_data = generate_ad_data()
    response = requests.post(f"{URL}/ads", json=ad_data)
    assert response.status_code == 201, f"Failed to create ad: {response.text}"
    ad_id = response.json()["id"]
    return {"ad_id": ad_id, "ad_data": ad_data}

class TestCreateAd:
    def test_create_ad_with_valid_data(self):
        """Проверка создания объявления с валидными данными"""
        ad_data = generate_ad_data()
        response = requests.post(f"{URL}/ads", json=ad_data)
        
        assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
        assert "id" in response.json(), "Response should contain ad ID"
        assert isinstance(response.json()["id"], int), "Ad ID should be an integer"
    
    def test_create_ad_without_required_fields(self):
        """Проверка создания объявления без обязательных полей"""
        ad_data = generate_ad_data()
        del ad_data["title"]
        
        response = requests.post(f"{URL}/ads", json=ad_data)
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    
    def test_create_ad_with_invalid_price(self):
        """Проверка создания объявления с некорректной ценой"""
        ad_data = generate_ad_data()
        ad_data["price"] = -100 
        
        response = requests.post(f"{URL}/ads", json=ad_data)
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    
    def test_create_ad_with_empty_description(self):
        """Проверка создания объявления с пустым описанием"""
        ad_data = generate_ad_data()
        ad_data["description"] = ""
        
        response = requests.post(f"{URL}/ads", json=ad_data)
        assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
        assert "id" in response.json(), "Response should contain ad ID"

class TestGetAdById:
    def test_get_existing_ad(self, create_ad):
        """Проверка получения существующего объявления по ID"""
        ad_id = create_ad["ad_id"]
        response = requests.get(f"{URL}/ads/{ad_id}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        ad_data = response.json()
        assert ad_data["id"] == ad_id, f"Expected ad ID {ad_id}, got {ad_data['id']}"
        assert ad_data["title"] == create_ad["ad_data"]["title"], "Title doesn't match"
        assert ad_data["description"] == create_ad["ad_data"]["description"], "Description doesn't match"
        assert ad_data["price"] == create_ad["ad_data"]["price"], "Price doesn't match"
        assert ad_data["sellerId"] == create_ad["ad_data"]["sellerId"], "Seller ID doesn't match"
    
    def test_get_nonexistent_ad(self):
        """Проверка получения несуществующего объявления по ID"""
        nonexistent_id = 9999999999
        response = requests.get(f"{URL}/ads/{nonexistent_id}")
        
        assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    def test_get_ad_with_invalid_id_format(self):
        """Проверка получения объявления по некорректному формату ID"""
        invalid_id = "invalid_id"
        response = requests.get(f"{URL}/ads/{invalid_id}")
        
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

class TestGetAdsBySellerId:
    def test_get_ads_by_existing_seller(self):
        """Проверка получения объявлений по существующему ID продавца"""
        seller_id = generate_seller_id()
        ads_count = 3
        created_ads = []
        
        for _ in range(ads_count):
            ad_data = generate_ad_data(seller_id)
            response = requests.post(f"{URL}/ads", json=ad_data)
            assert response.status_code == 201, f"Failed to create ad for seller {seller_id}"
            created_ads.append(response.json()["id"])
        
        response = requests.get(f"{URL}/ads/sellers/{seller_id}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        seller_ads = response.json()
        assert isinstance(seller_ads, list), "Response should be a list of ads"
        assert len(seller_ads) >= ads_count, f"Expected at least {ads_count} ads, got {len(seller_ads)}"
        
        ad_ids_in_response = [ad["id"] for ad in seller_ads]
        for ad_id in created_ads:
            assert ad_id in ad_ids_in_response, f"Ad {ad_id} not found in seller's ads"
    
    def test_get_ads_by_nonexistent_seller(self):
        """Проверка получения объявлений по несуществующему ID продавца"""
        nonexistent_seller_id = 999999999
        response = requests.get(f"{URL}/ads/sellers/{nonexistent_seller_id}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert isinstance(response.json(), list), "Response should be a list"
        assert len(response.json()) == 0, "Expected empty list for nonexistent seller"
    
    def test_get_ads_by_invalid_seller_id_format(self):
        """Проверка получения объявлений по некорректному формату ID продавца"""
        invalid_seller_id = "invalid_id"
        response = requests.get(f"{URL}/ads/sellers/{invalid_seller_id}")
        
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

class TestGetStatsByItemId:
    def test_get_stats_by_existing_item(self, create_ad):
        """Проверка получения статистики по существующему item ID"""
        item_id = create_ad["ad_data"]["itemId"]
        response = requests.get(f"{URL}/stats/{item_id}")
        
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        stats = response.json()
        
        assert "itemId" in stats, "Response should contain itemId"
        assert stats["itemId"] == item_id, f"Expected itemId {item_id}, got {stats['itemId']}"
        assert "views" in stats, "Response should contain views count"
        assert isinstance(stats["views"], int), "Views should be an integer"
    
    def test_get_stats_by_nonexistent_item(self):
        """Проверка получения статистики по несуществующему item ID"""
        nonexistent_item_id = 9999999999
        response = requests.get(f"{URL}/stats/{nonexistent_item_id}")
        
        if response.status_code == 200:
            stats = response.json()
            assert "itemId" in stats, "Response should contain itemId"
            assert stats["itemId"] == nonexistent_item_id, "Incorrect itemId in response"
            assert "views" in stats, "Response should contain views count"
            assert stats["views"] == 0, "Views should be 0 for nonexistent item"
        else:
            assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    
    def test_get_stats_with_invalid_item_id_format(self):
        """Проверка получения статистики по некорректному формату item ID"""
        invalid_item_id = "invalid_id"
        response = requests.get(f"{URL}/stats/{invalid_item_id}")
        
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

class TestEdgeCases:
    def test_create_multiple_ads_same_seller(self):
        """Проверка создания нескольких объявлений одним продавцом"""
        seller_id = generate_seller_id()
        ads_count = 5
        created_ad_ids = []
        
        for i in range(ads_count):
            ad_data = generate_ad_data(seller_id)
            ad_data["title"] = f"Test Ad {i+1} for Seller {seller_id}"
            
            response = requests.post(f"{URL}/ads", json=ad_data)
            assert response.status_code == 201, f"Failed to create ad {i+1} for seller {seller_id}"
            created_ad_ids.append(response.json()["id"])
        
        response = requests.get(f"{URL}/ads/sellers/{seller_id}")
        assert response.status_code == 200
        
        seller_ads = response.json()
        seller_ad_ids = [ad["id"] for ad in seller_ads]
        
        for ad_id in created_ad_ids:
            assert ad_id in seller_ad_ids, f"Ad {ad_id} not found in seller's ads list"
    
    def test_create_ad_with_large_values(self):
        """Проверка создания объявления с очень большими значениями полей"""
        ad_data = {
            "title": "A" * 1000, 
            "description": "B" * 5000,  
            "price": 1000000000,
            "sellerId": generate_seller_id(),
            "itemId": random.randint(1000000, 9999999)
        }
        
        response = requests.post(f"{URL}/ads", json=ad_data)
        assert response.status_code in [201, 400], f"Unexpected status code {response.status_code}"

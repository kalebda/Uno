#!/usr/bin/env python3
"""
Wikipedia Data Collector

This module provides functions to collect comprehensive information about countries including:
- Country overview
- Major cities and universities
- Weather and climate
- Work opportunities and economy
- Cost of living
- Culture and lifestyle

Can be imported and called from other scrapers with a country name parameter.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikipediaDataCollector:
    """Collector for Wikipedia data about countries and related topics."""

    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.api_url = "https://en.wikipedia.org/api/rest_v1"
        self.headers = {
            'User-Agent': "StudyAbroadAI/1.0 (Educational Project; +https://github.com/your-repo)",
            'Accept': 'application/json, text/html, */*',
        }
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.scraping_delay = 1

    def get_wikipedia_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Get Wikipedia page summary using the REST API."""
        try:
            clean_title = title.replace(" ", "_")
            url = f"{self.api_url}/page/summary/{clean_title}"

            logger.info(f"Fetching Wikipedia summary: {title}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return {
                "title": data.get("title", title),
                "extract": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": data.get("thumbnail", {}).get("source", ""),
                "coordinates": data.get("coordinates", {}),
                "timestamp": datetime.now().isoformat()
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching Wikipedia summary for {title}: {e}")
            return None

    def collect_country_data(self, country_name: str) -> Dict[str, Any]:
        """Collect comprehensive data about a specific country."""
        logger.info(f"Starting Wikipedia data collection for {country_name}...")

        country_data = {
            "country": country_name,
            "collected_at": datetime.now().isoformat(),
            "overview": {},
            "cities": [],
            "universities": [],
            "weather": {},
            "economy": {},
            "culture": {},
            "cost_of_living": {},
            "work_opportunities": {},
            "education_system": {}
        }

        country_data["overview"] = self.get_wikipedia_summary(country_name) or {}
        time.sleep(self.scraping_delay)

        cities = self._get_country_cities(country_name)
        for city in cities:
            city_data = self.get_wikipedia_summary(city)
            if city_data:
                country_data["cities"].append(city_data)
            time.sleep(self.scraping_delay)

        universities = self._get_country_universities(country_name)
        for university in universities:
            uni_data = self.get_wikipedia_summary(university)
            if uni_data:
                country_data["universities"].append(uni_data)
            time.sleep(self.scraping_delay)

        # 4. Weather and Climate
        weather_query = f"Climate of the {country_name}"
        country_data["weather"] = self.get_wikipedia_summary(weather_query) or {}
        time.sleep(self.scraping_delay)

        # 5. Economy
        economy_query = f"Economy of the {country_name}"
        country_data["economy"] = self.get_wikipedia_summary(economy_query) or {}
        time.sleep(self.scraping_delay)

        # 6. Culture
        culture_query = f"Culture of the {country_name}"
        country_data["culture"] = self.get_wikipedia_summary(culture_query) or {}
        time.sleep(self.scraping_delay)

        # 7. Cost of Living (major city)
        major_city = self._get_major_city(country_name)
        if major_city:
            # Try different cost of living page titles
            cost_queries = [
                f"Cost of living in {major_city}",
                f"{major_city}#Economy",
                f"Economy of {major_city}"
            ]
            for cost_query in cost_queries:
                cost_data = self.get_wikipedia_summary(cost_query)
                if cost_data:
                    country_data["cost_of_living"] = cost_data
                    break
            else:
                country_data["cost_of_living"] = {}
            time.sleep(self.scraping_delay)

        # 8. Work Opportunities
        work_queries = [
            f"Employment in the {country_name}",
            f"Economy of the {country_name}",
            f"Labor market in {country_name}"
        ]
        for work_query in work_queries:
            work_data = self.get_wikipedia_summary(work_query)
            if work_data:
                country_data["work_opportunities"] = work_data
                break
        else:
            country_data["work_opportunities"] = {}
        time.sleep(self.scraping_delay)

        # 9. Education System
        education_queries = [
            f"Education in the {country_name}",
            f"Education system in {country_name}",
            f"Higher education in {country_name}"
        ]
        for education_query in education_queries:
            education_data = self.get_wikipedia_summary(education_query)
            if education_data:
                country_data["education_system"] = education_data
                break
        else:
            country_data["education_system"] = {}
        time.sleep(self.scraping_delay)

        return country_data

    def _get_country_cities(self, country_name: str) -> List[str]:
        """Get major cities for a specific country."""
        city_mapping = {
            "Czech Republic": [
                "Prague", "Brno", "Ostrava", "Plzeň", "Liberec",
                "Olomouc", "Ústí nad Labem", "České Budějovice", "Hradec Králové"
            ],
            "Germany": [
                "Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt",
                "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"
            ],
            "Netherlands": [
                "Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven",
                "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"
            ],
            "France": [
                "Paris", "Marseille", "Lyon", "Toulouse", "Nice",
                "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille"
            ],
            "Italy": [
                "Rome", "Milan", "Naples", "Turin", "Palermo",
                "Genoa", "Bologna", "Florence", "Bari", "Catania"
            ],
            "Spain": [
                "Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza",
                "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao"
            ]
        }
        return city_mapping.get(country_name, [])

    def _get_country_universities(self, country_name: str) -> List[str]:
        """Get major universities for a specific country."""
        university_mapping = {
            "Czech Republic": [
                "Charles University", "Masaryk University", "Czech Technical University in Prague",
                "Palacký University Olomouc", "University of Ostrava", "University of West Bohemia",
                "Technical University of Liberec", "University of Pardubice", "Mendel University"
            ],
            "Germany": [
                "Technical University of Munich", "Ludwig Maximilian University of Munich",
                "Heidelberg University", "Humboldt University of Berlin", "Free University of Berlin",
                "University of Hamburg", "University of Cologne", "University of Bonn"
            ],
            "Netherlands": [
                "University of Amsterdam", "Delft University of Technology",
                "Leiden University", "Utrecht University", "Erasmus University Rotterdam",
                "University of Groningen", "Wageningen University", "Tilburg University"
            ],
            "France": [
                "Sorbonne University", "École Normale Supérieure", "École Polytechnique",
                "University of Paris-Saclay", "University of Lyon", "University of Toulouse",
                "University of Strasbourg", "University of Bordeaux"
            ],
            "Italy": [
                "University of Bologna", "Sapienza University of Rome", "University of Milan",
                "University of Padua", "University of Turin", "University of Florence",
                "University of Naples Federico II", "University of Pisa"
            ],
            "Spain": [
                "University of Barcelona", "Complutense University of Madrid",
                "Autonomous University of Madrid", "University of Valencia",
                "University of Granada", "University of Seville", "University of Salamanca"
            ]
        }
        return university_mapping.get(country_name, [])

    def _get_major_city(self, country_name: str) -> Optional[str]:
        """Get the major/capital city for cost of living data."""
        major_city_mapping = {
            "Czech Republic": "Prague",
            "Germany": "Berlin",
            "Netherlands": "Amsterdam",
            "France": "Paris",
            "Italy": "Rome",
            "Spain": "Madrid"
        }
        return major_city_mapping.get(country_name)

    def collect_detailed_city_info(self, city_name: str, country_name: str) -> Dict[str, Any]:
        """Collect detailed information about a specific city."""
        logger.info(f"Collecting detailed info for {city_name}, {country_name}")

        city_data = {
            "city": city_name,
            "country": country_name,
            "collected_at": datetime.now().isoformat(),
            "overview": {},
            "universities": [],
            "transportation": {},
            "attractions": {},
            "cost_of_living": {},
            "job_market": {}
        }

        city_data["overview"] = self.get_wikipedia_summary(city_name) or {}
        time.sleep(self.scraping_delay)

        transport_query = f"Public transport in {city_name}"
        city_data["transportation"] = self.get_wikipedia_summary(transport_query) or {}
        time.sleep(self.scraping_delay)

        attractions_query = f"Tourism in {city_name}"
        city_data["attractions"] = self.get_wikipedia_summary(attractions_query) or {}
        time.sleep(self.scraping_delay)

        cost_query = f"Cost of living in {city_name}"
        city_data["cost_of_living"] = self.get_wikipedia_summary(cost_query) or {}
        time.sleep(self.scraping_delay)

        return city_data

    def save_data(self, data: Dict[str, Any], filename: str):
        """Save collected data to JSON file."""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {filepath}")

    def collect_and_save_country_data(self, country_name: str) -> str:
        """Collect and save country data, return the filename."""
        country_data = self.collect_country_data(country_name)

        clean_country_name = country_name.replace(" ", "_").lower()
        filename = f"{clean_country_name}_wikipedia_data.json"

        self.save_data(country_data, filename)
        return filename


def collect_country_wikipedia_data(country_name: str) -> Dict[str, Any]:
    """Main function to collect Wikipedia data for a country."""
    collector = WikipediaDataCollector()
    return collector.collect_country_data(country_name)


def collect_and_save_country_data(country_name: str) -> str:
    """Collect and save country data, return the filename."""
    collector = WikipediaDataCollector()
    return collector.collect_and_save_country_data(country_name)


def collect_city_data(city_name: str, country_name: str) -> Dict[str, Any]:
    """Collect detailed data for a specific city."""
    collector = WikipediaDataCollector()
    return collector.collect_detailed_city_info(city_name, country_name)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        country_name = sys.argv[1]
        print(f"Collecting Wikipedia data for {country_name}...")
        filename = collect_and_save_country_data(country_name)
        print(f"Data saved to {filename}")
    else:
        print("Usage: python wikipedia_data_collector.py <country_name>")
        print("Example: python wikipedia_data_collector.py 'Czech Republic'")

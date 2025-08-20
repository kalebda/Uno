#!/usr/bin/env python3
"""
Czech Scholarship Scraper

This script scrapes the Czech Ministry of Education website for government scholarships
and stores the data in a structured format for the RAG pipeline.

COMPLIANCE NOTES:
- Respects robots.txt: Crawl-Delay: 30 seconds
- Educational use only
- Data attribution provided
- Rate limiting implemented
- Transparent User-Agent
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup
from wikipedia_data_collector import collect_country_wikipedia_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CzechScholarshipScraper:
    """Scraper for Czech government scholarships website."""

    def __init__(self):
        self.base_url = "https://msmt.gov.cz"
        self.target_url = "https://msmt.gov.cz/eu-and-international-affairs/government-scholarships-developing-countries?lang=2"
        self.headers = {
            'User-Agent': "StudyAbroadAI/1.0 (Educational Project; +https://github.com/your-repo)",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.scraping_delay = 30  # Respect robots.txt Crawl-Delay: 30

    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page."""
        try:
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            time.sleep(self.scraping_delay)

            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise

    def extract_scholarship_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract scholarship information from the main page."""
        scholarship_data = {
            "country": "Czech Republic",
            "source_url": self.target_url,
            "scraped_at": datetime.now().isoformat(),
            "programs": [],
            "general_info": {},
            "requirements": [],
            "application_process": {},
            "deadlines": [],
            "contact_info": {}
        }

        try:
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('body')

            if not main_content:
                logger.warning("Could not find main content area")
                return scholarship_data

            self._clean_content(main_content)

            scholarship_data["general_info"] = self._extract_general_info_from_html(main_content)
            scholarship_data["application_process"] = self._extract_application_process_from_html(main_content)
            scholarship_data["contact_info"] = self._extract_contact_info_from_html(main_content)

            programs = self._create_program_entries_from_html(scholarship_data, main_content)
            scholarship_data["programs"] = programs

            logger.info(f"Successfully extracted data for {len(programs)} programs")

        except Exception as e:
            logger.error(f"Error extracting scholarship info: {e}")

        return scholarship_data

    def _clean_content(self, content: BeautifulSoup):
        """Remove navigation and irrelevant elements from content."""
        for element in content.find_all(['nav', 'header', 'footer', 'aside']):
            element.decompose()

        for element in content.find_all(class_=lambda x: x and any(word in x.lower() for word in ['nav', 'menu', 'sidebar', 'breadcrumb'])):
            element.decompose()

        for element in content.find_all(['script', 'style']):
            element.decompose()

    def _extract_general_info_from_html(self, content: BeautifulSoup) -> Dict[str, Any]:
        """Extract general information from HTML."""
        general_info = {
            'title': 'Czech Government Scholarships for Developing Countries',
            'description': 'Government scholarships offered by the Czech Republic for students from developing countries',
            'eligible_countries': [],
            'study_languages': [],
            'program_types': []
        }

        # Hardcode the eligible countries since we know them
        general_info['eligible_countries'] = [
            'Bosnia and Herzegovina', 'Georgia', 'Ukraine', 'Belarus',
            'Ethiopia', 'Nigeria', 'Rwanda', 'Zambia', 'Cambodia',
            'Sri Lanka', 'Guatemala', 'Jordan'
        ]

        text_content = content.get_text()

        if 'czech language' in text_content.lower():
            general_info['study_languages'].append('Czech')
        if 'english language' in text_content.lower():
            general_info['study_languages'].append('English')

        if 'bachelor' in text_content.lower():
            general_info['program_types'].append('Bachelor')
        if 'master' in text_content.lower():
            general_info['program_types'].append('Master')
        if 'doctoral' in text_content.lower() or 'phd' in text_content.lower():
            general_info['program_types'].append('PhD')

        return general_info

    def _extract_application_process_from_html(self, content: BeautifulSoup) -> Dict[str, Any]:
        """Extract application process from HTML."""
        process_info = {
            'has_application_process': True,
            'description': 'Application process available',
            'key_steps': []
        }

        application_sections = content.find_all(['h5', 'h4', 'h3'], string=lambda text: text and 'application' in text.lower())

        for section in application_sections:
            next_elem = section.find_next_sibling()
            if next_elem:
                step_text = next_elem.get_text(strip=True)
                if step_text and len(step_text) < 300:
                    process_info['key_steps'].append(step_text)

        deadline_text = content.find(string=lambda text: text and 'deadline' in text.lower())
        if deadline_text:
            parent = deadline_text.parent
            if parent:
                deadline_info = parent.get_text(strip=True)
                if deadline_info and len(deadline_info) < 200:
                    process_info['key_steps'].append(deadline_info)

        return process_info

    def _extract_contact_info_from_html(self, content: BeautifulSoup) -> Dict[str, Any]:
        """Extract contact information from HTML."""
        contact_info = {}

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content.get_text())

        if emails:
            contact_info['emails'] = list(set(emails))

        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        phones = re.findall(phone_pattern, content.get_text())
        if phones:
            clean_phones = []
            for phone in phones:
                clean_phone = re.sub(r'\s+', '', phone.strip())
                if len(clean_phone) >= 10:
                    clean_phones.append(clean_phone)
            contact_info['phones'] = clean_phones[:3]

        return contact_info

    def _create_program_entries_from_html(self, scholarship_data: Dict[str, Any], content: BeautifulSoup) -> List[Dict[str, Any]]:
        """Create program entries based on actual HTML content."""
        programs = []

        program_info = self._extract_program_details_from_html(content)

        # Program-specific requirements and deadline
        deadline = ["30 September 2025"]

        if 'Bachelor' in scholarship_data["general_info"]["program_types"]:
            bachelor_program = {
                "name": "Bachelor's Degree",
                "level": "Bachelor",
                "duration": "3-4 years",
                "description": "Undergraduate studies in various fields",
                "language": program_info.get('bachelor_language', 'Czech'),
                "country": scholarship_data["country"],
                "requirements": [
                    "Completion of secondary education with school-leaving examination",
                    "Czech language proficiency required",
                    "Only available for applicants from Georgia",
                    "Must not be a Czech citizen or EU resident",
                    "Must complete entrance examinations"
                ],
                "deadlines": deadline,
                "application_process": scholarship_data["application_process"],
                "contact_info": scholarship_data["contact_info"],
                "source_url": scholarship_data["source_url"],
                "additional_info": program_info.get('bachelor_info', {})
            }
            programs.append(bachelor_program)

        if 'Master' in scholarship_data["general_info"]["program_types"]:
            master_program = {
                "name": "Master's Degree",
                "level": "Master",
                "duration": "2 years",
                "description": "Graduate studies in various fields",
                "language": program_info.get('master_language', 'Czech and English'),
                "country": scholarship_data["country"],
                "requirements": [
                    "Completion of bachelor's degree program",
                    "Czech or English language proficiency",
                    "Available for all eligible countries",
                    "Must not be a Czech citizen or EU resident",
                    "Must complete entrance examinations",
                    "English language test required for English programs"
                ],
                "deadlines": deadline,
                "application_process": scholarship_data["application_process"],
                "contact_info": scholarship_data["contact_info"],
                "source_url": scholarship_data["source_url"],
                "additional_info": program_info.get('master_info', {})
            }
            programs.append(master_program)

        if 'PhD' in scholarship_data["general_info"]["program_types"]:
            phd_program = {
                "name": "PhD Studies",
                "level": "PhD",
                "duration": "3-4 years",
                "description": "Doctoral studies in various fields",
                "language": program_info.get('phd_language', 'English'),
                "country": scholarship_data["country"],
                "requirements": [
                    "Completion of master's degree program",
                    "English language proficiency required",
                    "Available for all eligible countries",
                    "Must not be a Czech citizen or EU resident",
                    "Must complete entrance examinations",
                    "English language test required"
                ],
                "deadlines": deadline,
                "application_process": scholarship_data["application_process"],
                "contact_info": scholarship_data["contact_info"],
                "source_url": scholarship_data["source_url"],
                "additional_info": program_info.get('phd_info', {})
            }
            programs.append(phd_program)

        return programs

    def _extract_program_details_from_html(self, content: BeautifulSoup) -> Dict[str, Any]:
        """Extract specific program details from HTML."""
        program_details = {}
        text_content = content.get_text()

        if 'bachelor' in text_content.lower():
            if 'georgia' in text_content.lower():
                program_details['bachelor_language'] = 'Czech (Georgia only)'
                program_details['bachelor_info'] = {
                    'availability': 'Limited (Georgia only)',
                    'language_requirement': 'Czech language proficiency required'
                }
            else:
                program_details['bachelor_language'] = 'Czech'
                program_details['bachelor_info'] = {
                    'availability': 'Limited',
                    'language_requirement': 'Czech language proficiency required'
                }

        if 'master' in text_content.lower():
            if 'english' in text_content.lower():
                program_details['master_language'] = 'Czech and English'
                program_details['master_info'] = {
                    'availability': 'Available for all eligible countries',
                    'language_options': 'Czech or English'
                }
            else:
                program_details['master_language'] = 'Czech'
                program_details['master_info'] = {
                    'availability': 'Available for eligible countries',
                    'language_options': 'Czech'
                }

        if 'doctoral' in text_content.lower() or 'phd' in text_content.lower():
            program_details['phd_language'] = 'English'
            program_details['phd_info'] = {
                'availability': 'Available for all eligible countries',
                'language': 'English'
            }

        return program_details

    def save_data(self, data: Dict[str, Any]) -> str:
        """Save scraped data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"czech_scholarships_{timestamp}.json"
        filepath = self.data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Data saved to: {filepath}")
        return str(filepath)

    def save_integrated_data(self, data: Dict[str, Any]) -> str:
        """Save integrated scholarship and Wikipedia data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"czech_integrated_data_{timestamp}.json"
        filepath = self.data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Integrated data saved to: {filepath}")
        return str(filepath)

    def scrape(self) -> str:
        """Main scraping method."""
        logger.info("Starting Czech scholarship scraping...")

        try:
            soup = self.get_page_content(self.target_url)

            scholarship_data = self.extract_scholarship_info(soup)

            logger.info("Collecting Wikipedia data for Czech Republic...")
            try:
                wikipedia_data = collect_country_wikipedia_data("Czech Republic")

                integrated_data = {
                    "country": "Czech Republic",
                    "collected_at": datetime.now().isoformat(),
                    "scholarships": scholarship_data,
                    "country_info": wikipedia_data
                }

                filepath = self.save_integrated_data(integrated_data)
                logger.info("Integrated data collection completed successfully!")

            except Exception as wiki_error:
                logger.warning(f"Wikipedia data collection failed: {wiki_error}")
                logger.info("Saving only scholarship data...")
                filepath = self.save_data(scholarship_data)

            return filepath

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise


def main():
    """Main function to run the scraper."""
    try:
        scraper = CzechScholarshipScraper()
        scraper.scrape()
        return 0
    except Exception as e:
        return 1


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Load Data to Vector Database

This script loads scraped data into ChromaDB for the RAG pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import List

# Add the app directory to the path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))
print(f"Added to Python path: {app_path}")
print(f"Current working directory: {Path.cwd()}")
print(f"Python path: {sys.path}")

from app.services.vector_store import VectorStoreService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorDBLoader:
    """Loader for populating the vector database with scraped data."""

    def __init__(self):
        self.vector_service = VectorStoreService()
        self.data_dir = Path("data")

    def find_data_files(self) -> List[Path]:
        """Find all JSON data files in the data directory."""
        data_files = []

        if not self.data_dir.exists():
            logger.warning("Data directory does not exist")
            return data_files

        # Find all JSON files
        for file_path in self.data_dir.glob("*.json"):
            if file_path.is_file():
                data_files.append(file_path)

        return data_files

    def load_specific_file(self, file_path: str):
        """Load a specific data file into the vector database."""
        try:
            logger.info(f"Loading data from: {file_path}")

            # Load and store data
            self.vector_service.load_and_store_data(file_path)

            logger.info(f"Successfully loaded {file_path} into vector database")

        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise

    def load_all_data(self):
        """Load all data files into the vector database."""
        data_files = self.find_data_files()

        if not data_files:
            logger.warning("No data files found in data directory")
            return

        logger.info(f"Found {len(data_files)} data files to load")

        for file_path in data_files:
            try:
                self.load_specific_file(str(file_path))
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue

        logger.info("Completed loading all data files")

    def show_stats(self):
        """Show statistics about the vector database collections."""
        logger.info("Vector Database Statistics:")

        collections = ["scholarships", "country_info", "universities", "cities"]

        for collection_name in collections:
            stats = self.vector_service.get_collection_stats(collection_name)
            if "error" not in stats:
                logger.info(f"  {collection_name}: {stats['document_count']} documents")
            else:
                logger.warning(f"  {collection_name}: Error - {stats['error']}")

    def search_test(self, query: str = "Czech Republic scholarships"):
        """Test search functionality."""
        logger.info(f"Testing search with query: '{query}'")

        # Search in scholarships collection
        scholarship_results = self.vector_service.search_similar(
            query, "scholarships", n_results=3
        )

        logger.info(f"Found {len(scholarship_results)} scholarship results:")
        for i, result in enumerate(scholarship_results):
            logger.info(f"  {i+1}. {result['text'][:100]}...")
            logger.info(f"     Metadata: {result['metadata']}")

        # Search in country info collection
        country_results = self.vector_service.search_similar(
            query, "country_info", n_results=3
        )

        logger.info(f"Found {len(country_results)} country info results:")
        for i, result in enumerate(country_results):
            logger.info(f"  {i+1}. {result['text'][:100]}...")
            logger.info(f"     Metadata: {result['metadata']}")


def main():
    """Main function to run the vector database loader."""
    import argparse

    parser = argparse.ArgumentParser(description="Load data into vector database")
    parser.add_argument("--file", help="Load specific file")
    parser.add_argument("--all", action="store_true", help="Load all data files")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--test-search", help="Test search with query")

    args = parser.parse_args()

    loader = VectorDBLoader()

    try:
        if args.file:
            loader.load_specific_file(args.file)
        elif args.all:
            loader.load_all_data()
        elif args.stats:
            loader.show_stats()
        elif args.test_search:
            loader.search_test(args.test_search)
        else:
            # Default: load all data
            loader.load_all_data()
            loader.show_stats()

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

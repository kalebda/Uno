"""
Vector Store Service using ChromaDB

This module handles vector database operations including:
- Data chunking and preprocessing
- Vector storage and retrieval
- Similarity search
- Document management
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector database operations with ChromaDB."""

    def __init__(self):
        self.vector_db_path = Path(settings.VECTOR_DB_PATH)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )

        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collections = {
            "scholarships": "scholarships_collection",
            "country_info": "country_info_collection",
            "universities": "universities_collection",
            "cities": "cities_collection"
        }

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata."""
        if not text or not text.strip():
            return []

        chunks = self.text_splitter.split_text(text)
        chunked_documents = []

        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_id": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            })

            chunked_documents.append({
                "text": chunk,
                "metadata": chunk_metadata
            })

        return chunked_documents

    def process_scholarship_data(self, scholarship_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process scholarship data into chunks for vector storage."""
        documents = []

        # Process general scholarship information
        if "general_info" in scholarship_data:
            general_text = self._extract_text_from_dict(scholarship_data["general_info"])
            if general_text:
                metadata = {
                    "type": "scholarship_general",
                    "country": scholarship_data.get("country", "Unknown"),
                    "source": "scholarship_scraper",
                    "category": "general_info"
                }
                chunks = self.chunk_text(general_text, metadata)
                documents.extend(chunks)

        # Process individual programs
        if "programs" in scholarship_data:
            for i, program in enumerate(scholarship_data["programs"]):
                program_text = self._extract_text_from_dict(program)
                if program_text:
                    metadata = {
                        "type": "scholarship_program",
                        "country": scholarship_data.get("country", "Unknown"),
                        "program_name": program.get("name", f"Program {i}"),
                        "program_level": program.get("level", "Unknown"),
                        "source": "scholarship_scraper",
                        "category": "program_details"
                    }
                    chunks = self.chunk_text(program_text, metadata)
                    documents.extend(chunks)

        # Process requirements
        if "requirements" in scholarship_data:
            requirements_text = "\n".join(scholarship_data["requirements"])
            if requirements_text:
                metadata = {
                    "type": "scholarship_requirements",
                    "country": scholarship_data.get("country", "Unknown"),
                    "source": "scholarship_scraper",
                    "category": "requirements"
                }
                chunks = self.chunk_text(requirements_text, metadata)
                documents.extend(chunks)

        return documents

    def process_country_data(self, country_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process country information data into chunks."""
        documents = []

        # Process country overview
        if "overview" in country_data and country_data["overview"].get("extract"):
            overview_text = country_data["overview"]["extract"]
            metadata = {
                "type": "country_overview",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "overview"
            }
            chunks = self.chunk_text(overview_text, metadata)
            documents.extend(chunks)

        # Process cities
        if "cities" in country_data:
            for city in country_data["cities"]:
                if city.get("extract"):
                    city_text = city["extract"]
                    metadata = {
                        "type": "city_info",
                        "country": country_data.get("country", "Unknown"),
                        "city": city.get("title", "Unknown"),
                        "source": "wikipedia",
                        "category": "cities"
                    }
                    chunks = self.chunk_text(city_text, metadata)
                    documents.extend(chunks)

        # Process universities
        if "universities" in country_data:
            for university in country_data["universities"]:
                if university.get("extract"):
                    uni_text = university["extract"]
                    metadata = {
                        "type": "university_info",
                        "country": country_data.get("country", "Unknown"),
                        "university": university.get("title", "Unknown"),
                        "source": "wikipedia",
                        "category": "universities"
                    }
                    chunks = self.chunk_text(uni_text, metadata)
                    documents.extend(chunks)

        # Process weather/climate
        if "weather" in country_data and country_data["weather"].get("extract"):
            weather_text = country_data["weather"]["extract"]
            metadata = {
                "type": "weather_info",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "weather"
            }
            chunks = self.chunk_text(weather_text, metadata)
            documents.extend(chunks)

        # Process economy
        if "economy" in country_data and country_data["economy"].get("extract"):
            economy_text = country_data["economy"]["extract"]
            metadata = {
                "type": "economy_info",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "economy"
            }
            chunks = self.chunk_text(economy_text, metadata)
            documents.extend(chunks)

        # Process culture
        if "culture" in country_data and country_data["culture"].get("extract"):
            culture_text = country_data["culture"]["extract"]
            metadata = {
                "type": "culture_info",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "culture"
            }
            chunks = self.chunk_text(culture_text, metadata)
            documents.extend(chunks)

        # Process cost of living
        if "cost_of_living" in country_data and country_data["cost_of_living"].get("extract"):
            cost_text = country_data["cost_of_living"]["extract"]
            metadata = {
                "type": "cost_of_living",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "cost_of_living"
            }
            chunks = self.chunk_text(cost_text, metadata)
            documents.extend(chunks)

        # Process work opportunities
        if "work_opportunities" in country_data and country_data["work_opportunities"].get("extract"):
            work_text = country_data["work_opportunities"]["extract"]
            metadata = {
                "type": "work_opportunities",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "work_opportunities"
            }
            chunks = self.chunk_text(work_text, metadata)
            documents.extend(chunks)

        # Process education system
        if "education_system" in country_data and country_data["education_system"].get("extract"):
            education_text = country_data["education_system"]["extract"]
            metadata = {
                "type": "education_system",
                "country": country_data.get("country", "Unknown"),
                "source": "wikipedia",
                "category": "education_system"
            }
            chunks = self.chunk_text(education_text, metadata)
            documents.extend(chunks)

        return documents

    def _extract_text_from_dict(self, data: Dict[str, Any]) -> str:
        """Extract text content from a dictionary structure."""
        if isinstance(data, str):
            return data

        text_parts = []

        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                text_parts.append(f"{key}: {value}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        text_parts.append(self._extract_text_from_dict(item))
            elif isinstance(value, dict):
                text_parts.append(self._extract_text_from_dict(value))

        return "\n".join(text_parts)

    def store_documents(self, documents: List[Dict[str, Any]], collection_name: str = "scholarships"):
        """Store documents in the vector database."""
        if not documents:
            logger.warning("No documents to store")
            return

        try:
            # Get or create collection
            collection = self.client.get_or_create_collection(
                name=self.collections.get(collection_name, collection_name)
            )

            # Prepare data for ChromaDB
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            ids = [f"{collection_name}_{i}" for i in range(len(documents))]

            # Add documents to collection
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Stored {len(documents)} documents in collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise

    def search_similar(self, query: str, collection_name: str = "scholarships",
                       n_results: int = 5, filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database."""
        try:
            collection = self.client.get_collection(
                name=self.collections.get(collection_name, collection_name)
            )

            # Prepare where clause for filtering
            where_clause = None
            if filter_metadata:
                where_clause = {}
                for key, value in filter_metadata.items():
                    where_clause[key] = value

            # Search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )

            # Format results
            formatted_results = []
            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def load_and_store_data(self, data_file_path: str):
        """Load data from JSON file and store in vector database."""
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Process scholarship data
            if "scholarships" in data:
                scholarship_docs = self.process_scholarship_data(data["scholarships"])
                self.store_documents(scholarship_docs, "scholarships")

            # Process country information
            if "country_info" in data:
                country_docs = self.process_country_data(data["country_info"])
                self.store_documents(country_docs, "country_info")

            logger.info(f"Successfully processed and stored data from {data_file_path}")

        except Exception as e:
            logger.error(f"Error loading and storing data: {e}")
            raise

    def get_collection_stats(self, collection_name: str = "scholarships") -> Dict[str, Any]:
        """Get statistics about a collection."""
        try:
            collection = self.client.get_collection(
                name=self.collections.get(collection_name, collection_name)
            )

            count = collection.count()

            return {
                "collection_name": collection_name,
                "document_count": count,
                "collection_type": "persistent"
            }

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    def clear_collection(self, collection_name: str = "scholarships"):
        """Clear all documents from a collection."""
        try:
            collection = self.client.get_collection(
                name=self.collections.get(collection_name, collection_name)
            )
            collection.delete()
            logger.info(f"Cleared collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

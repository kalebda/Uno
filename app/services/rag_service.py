"""
RAG (Retrieval-Augmented Generation) Service

This service combines vector database retrieval with LLM generation
to provide intelligent, context-aware responses about study opportunities.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.prompt_builder import prompt_builder
from app.services.groq_service import GroqService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for intelligent study abroad assistance."""

    def __init__(self):
        self.groq_service = GroqService()
        self.vector_service = VectorStoreService()

    def generate_response(self, user_query: str, user_background: Dict[str, Any] = None, chat_history: List = None) -> Dict[str, Any]:
        """Generate a comprehensive response using RAG."""
        try:
            # Step 1: Retrieve relevant documents
            relevant_docs = self._retrieve_relevant_documents(user_query)

            # Step 2: Create context from retrieved documents
            context = self._create_context_from_documents(relevant_docs)

            # Step 3: Generate response using LLM with chat history
            response = self._generate_llm_response(user_query, context, user_background, chat_history)

            return {
                "response": response,
                "query": user_query,
                "user_background": user_background,
                "sources": self._extract_sources(relevant_docs),
                "confidence": self._calculate_confidence(relevant_docs)
            }

        except Exception as e:
            logger.error(f"Error in RAG response generation: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again.",
                "error": str(e)
            }

    def _retrieve_relevant_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from vector database."""
        relevant_docs = []

        # Search in scholarships collection
        scholarship_results = self.vector_service.search_similar(
            query, "scholarships", n_results=n_results
        )
        relevant_docs.extend(scholarship_results)

        # Search in country info collection
        country_results = self.vector_service.search_similar(
            query, "country_info", n_results=n_results
        )
        relevant_docs.extend(country_results)

        # Sort by relevance (distance) if available
        relevant_docs.sort(key=lambda x: x.get('distance', 1.0))

        return relevant_docs[:n_results * 2]  # Return top results

    def _create_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Create context string from retrieved documents."""
        if not documents:
            return "No relevant information found."

        context_parts = []

        for i, doc in enumerate(documents):
            metadata = doc.get('metadata', {})
            doc_type = metadata.get('type', 'unknown')
            source = metadata.get('source', 'unknown')

            context_parts.append(f"Document {i+1} ({doc_type}, source: {source}):")
            context_parts.append(doc.get('text', ''))
            context_parts.append("")  # Empty line for separation

        return "\n".join(context_parts)

    def _generate_llm_response(self, query: str, context: str, user_background: Dict[str, Any] = None, chat_history: List = None) -> str:
        """Generate response using Groq LLM with context and chat history."""

        # Build prompts using prompt builder
        system_prompt, user_message = prompt_builder.build_chat_prompt(
            query=query,
            context=context,
            user_background=user_background,
            chat_history=chat_history
        )

        return self.groq_service.get_response(user_message, system_prompt)

    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from documents."""
        sources = []

        for doc in documents:
            metadata = doc.get('metadata', {})
            source_info = {
                "type": metadata.get('type', 'unknown'),
                "source": metadata.get('source', 'unknown'),
                "country": metadata.get('country', 'unknown'),
                "category": metadata.get('category', 'unknown')
            }

            # Add specific source details
            if metadata.get('university'):
                source_info['university'] = metadata['university']
            if metadata.get('city'):
                source_info['city'] = metadata['city']
            if metadata.get('program_name'):
                source_info['program_name'] = metadata['program_name']

            sources.append(source_info)

        return sources

    def _calculate_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on document relevance."""
        if not documents:
            return 0.0

        # Calculate average distance (lower is better)
        distances = [doc.get('distance', 1.0) for doc in documents]
        avg_distance = sum(distances) / len(distances)

        # Convert distance to confidence (0-1 scale)
        # Assuming distances are typically 0-2, with 0 being perfect match
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))

        return round(confidence, 2)

    def analyze_scholarship_fit(self, user_background: Dict[str, Any], scholarship_query: str = None) -> Dict[str, Any]:
        """Analyze if a user fits specific scholarship programs."""
        try:
            # Retrieve scholarship information
            if scholarship_query:
                relevant_docs = self.vector_service.search_similar(
                    scholarship_query, "scholarships", n_results=10
                )
            else:
                # Get general scholarship information
                relevant_docs = self.vector_service.search_similar(
                    "scholarship requirements eligibility", "scholarships", n_results=10
                )

            context = self._create_context_from_documents(relevant_docs)

            # Build prompts using prompt builder
            system_prompt, user_message = prompt_builder.build_scholarship_analysis_prompt(
                user_background=user_background,
                context=context
            )

            analysis = self.groq_service.get_response(user_message, system_prompt)

            return {
                "analysis": analysis,
                "user_background": user_background,
                "scholarship_query": scholarship_query,
                "sources": self._extract_sources(relevant_docs),
                "confidence": self._calculate_confidence(relevant_docs)
            }

        except Exception as e:
            logger.error(f"Error in scholarship fit analysis: {e}")
            return {
                "analysis": "I apologize, but I encountered an error while analyzing your eligibility. Please try again.",
                "error": str(e)
            }

    def get_country_information(self, country_name: str, info_type: str = "general") -> Dict[str, Any]:
        """Get specific country information."""
        try:
            # Search for country-specific information
            query = f"{country_name} {info_type}"
            relevant_docs = self.vector_service.search_similar(
                query, "country_info", n_results=5
            )

            context = self._create_context_from_documents(relevant_docs)

            # Build prompts using prompt builder
            system_prompt, user_message = prompt_builder.build_country_info_prompt(
                country_name=country_name,
                info_type=info_type,
                context=context
            )

            response = self.groq_service.get_response(user_message, system_prompt)

            return {
                "country": country_name,
                "info_type": info_type,
                "information": response,
                "sources": self._extract_sources(relevant_docs),
                "confidence": self._calculate_confidence(relevant_docs)
            }

        except Exception as e:
            logger.error(f"Error getting country information: {e}")
            return {
                "country": country_name,
                "info_type": info_type,
                "information": f"I apologize, but I encountered an error while retrieving information about {country_name}.",
                "error": str(e)
            }

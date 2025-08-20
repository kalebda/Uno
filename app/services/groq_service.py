from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import settings


class GroqService:
    """Service for interacting with Groq LLM."""

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-8b-8192"
        )

    def get_response(self, user_message: str, system_prompt: str = None) -> str:
        """Get response from Groq LLM."""
        if not settings.GROQ_API_KEY:
            return "Groq API key not configured"

        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=user_message))

            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error getting response from Groq: {str(e)}"

    def analyze_scholarship_fit(self, user_background: dict, scholarship_info: dict) -> str:
        """Analyze if a user fits a specific scholarship program."""
        system_prompt = """You are a helpful AI assistant that analyzes scholarship eligibility. 
        You should evaluate if a user's background matches the requirements for a specific scholarship program.
        Provide a clear assessment with specific reasons for eligibility or ineligibility."""

        user_message = f"""
        User Background: {user_background}
        
        Scholarship Information: {scholarship_info}
        
        Please analyze if this user is eligible for this scholarship program and provide specific recommendations.
        """

        return self.get_response(user_message, system_prompt)

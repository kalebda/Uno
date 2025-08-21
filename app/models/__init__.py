# Import all models here to ensure they are registered with SQLAlchemy

from app.db.base_class import Base

from .chat_message import ChatMessage
# Import all models
from .user import User

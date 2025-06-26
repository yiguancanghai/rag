from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

from utils.logger import logger


class ChatManager:
    """Manage chat history and conversation state"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.chat_history: List[Dict] = []
        self.favorites: List[Dict] = []
        self.chat_file = Path(f"./data/chat_history_{session_id}.json")
        self.favorites_file = Path(f"./data/favorites_{session_id}.json")
        
        # Create data directory
        self.chat_file.parent.mkdir(exist_ok=True)
        
        # Load existing history
        self._load_chat_history()
        self._load_favorites()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Add a message to chat history"""
        message = {
            "id": f"{datetime.now().timestamp()}_{len(self.chat_history)}",
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.chat_history.append(message)
        self._save_chat_history()
        
        logger.info(f"Added {role} message to chat history")
        return message
    
    def add_qa_pair(self, question: str, answer: str, source_docs: List[Dict], 
                   confidence_score: float) -> Dict:
        """Add a question-answer pair to chat history"""
        # Add user question
        self.add_message("user", question)
        
        # Add assistant answer with metadata
        metadata = {
            "source_documents": source_docs,
            "confidence_score": confidence_score,
            "document_count": len(source_docs)
        }
        
        return self.add_message("assistant", answer, metadata)
    
    def get_chat_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get chat history with optional limit"""
        if limit:
            return self.chat_history[-limit:]
        return self.chat_history
    
    def get_conversation_context(self, limit: int = 5) -> str:
        """Get recent conversation context for LLM"""
        recent_messages = self.chat_history[-limit:]
        
        context = ""
        for msg in recent_messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n\n"
        
        return context.strip()
    
    def clear_history(self) -> bool:
        """Clear chat history"""
        try:
            self.chat_history = []
            self._save_chat_history()
            logger.info("Chat history cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
            return False
    
    def add_to_favorites(self, message_id: str, title: Optional[str] = None) -> bool:
        """Add a message to favorites"""
        try:
            # Find the message
            message = next((msg for msg in self.chat_history if msg["id"] == message_id), None)
            if not message:
                return False
            
            # Create favorite entry
            favorite = {
                "id": message_id,
                "title": title or message["content"][:100] + "...",
                "question": "",
                "answer": message["content"],
                "timestamp": message["timestamp"],
                "added_to_favorites": datetime.now().isoformat()
            }
            
            # Find the corresponding question if this is an answer
            if message["role"] == "assistant":
                # Look for the previous user message
                msg_index = next((i for i, msg in enumerate(self.chat_history) 
                                if msg["id"] == message_id), -1)
                if msg_index > 0 and self.chat_history[msg_index - 1]["role"] == "user":
                    favorite["question"] = self.chat_history[msg_index - 1]["content"]
            
            # Add to favorites if not already there
            if not any(fav["id"] == message_id for fav in self.favorites):
                self.favorites.append(favorite)
                self._save_favorites()
                logger.info(f"Added message to favorites: {message_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return False
    
    def get_favorites(self) -> List[Dict]:
        """Get all favorites"""
        return self.favorites
    
    def remove_from_favorites(self, message_id: str) -> bool:
        """Remove a message from favorites"""
        try:
            self.favorites = [fav for fav in self.favorites if fav["id"] != message_id]
            self._save_favorites()
            logger.info(f"Removed message from favorites: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing from favorites: {str(e)}")
            return False
    
    def get_chat_statistics(self) -> Dict:
        """Get chat statistics"""
        if not self.chat_history:
            return {"total_messages": 0, "user_messages": 0, "assistant_messages": 0}
        
        user_messages = sum(1 for msg in self.chat_history if msg["role"] == "user")
        assistant_messages = sum(1 for msg in self.chat_history if msg["role"] == "assistant")
        
        return {
            "total_messages": len(self.chat_history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "favorites_count": len(self.favorites),
            "first_message_date": self.chat_history[0]["timestamp"] if self.chat_history else None,
            "last_message_date": self.chat_history[-1]["timestamp"] if self.chat_history else None
        }
    
    def search_history(self, query: str, limit: int = 10) -> List[Dict]:
        """Search chat history"""
        query_lower = query.lower()
        
        matching_messages = []
        for msg in self.chat_history:
            if query_lower in msg["content"].lower():
                matching_messages.append(msg)
        
        return matching_messages[-limit:]
    
    def _save_chat_history(self):
        """Save chat history to file"""
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}")
    
    def _load_chat_history(self):
        """Load chat history from file"""
        try:
            if self.chat_file.exists():
                with open(self.chat_file, 'r', encoding='utf-8') as f:
                    self.chat_history = json.load(f)
                logger.info(f"Loaded {len(self.chat_history)} messages from history")
        except Exception as e:
            logger.error(f"Error loading chat history: {str(e)}")
            self.chat_history = []
    
    def _save_favorites(self):
        """Save favorites to file"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving favorites: {str(e)}")
    
    def _load_favorites(self):
        """Load favorites from file"""
        try:
            if self.favorites_file.exists():
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
                logger.info(f"Loaded {len(self.favorites)} favorites")
        except Exception as e:
            logger.error(f"Error loading favorites: {str(e)}")
            self.favorites = []
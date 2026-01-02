
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat sessions and history storage"""
    
    def __init__(self, data_dir: Path):
        self.chats_dir = data_dir / "chats"
        self.chats_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.chats_dir / "metadata.json"
        self._ensure_metadata()
        
    def _ensure_metadata(self):
        """Ensure the metadata file exists"""
        if not self.metadata_file.exists():
            self._save_metadata([])

    def _load_metadata(self) -> List[Dict]:
        """Load list of all chats"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat metadata: {e}")
            return []

    def _save_metadata(self, metadata: List[Dict]):
        """Save list of all chats"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save chat metadata: {e}")

    def create_chat(self, title: str = "New Chat", user_id: int = None) -> Dict:
        """Create a new chat session
        
        Args:
            title: Chat title
            user_id: ID of user who owns this chat
        """
        chat_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # Entry for metadata list
        meta_entry = {
            "id": chat_id,
            "title": title,
            "created_at": created_at,
            "updated_at": created_at,
            "user_id": user_id  # Add user_id to metadata
        }
        
        # Update metadata
        metadata = self._load_metadata()
        metadata.insert(0, meta_entry) # Prepend
        self._save_metadata(metadata)
        
        # Create empty chat file
        self.save_messages(chat_id, [])
        
        return meta_entry

    def get_chats(self) -> List[Dict]:
        """Get all chat sessions (metadata) - deprecated, use get_user_chats"""
        return self._load_metadata()
    
    def get_user_chats(self, user_id: int) -> List[Dict]:
        """Get chat sessions for a specific user
        
        Args:
            user_id: User ID to filter chats
            
        Returns:
            List of chat metadata for the specified user
        """
        all_chats = self._load_metadata()
        return [chat for chat in all_chats if chat.get('user_id') == user_id]
    
    def get_all_chats_grouped(self) -> Dict[int, List[Dict]]:
        """Get all chats grouped by user (for admin view)
        
        Returns:
            Dictionary mapping user_id -> list of chats
        """
        all_chats = self._load_metadata()
        grouped = {}
        for chat in all_chats:
            uid = chat.get('user_id')
            if uid not in grouped:
                grouped[uid] = []
            grouped[uid].append(chat)
        return grouped

    def get_messages(self, chat_id: str) -> List[Dict]:
        """Get messages for a specific chat"""
        chat_file = self.chats_dir / f"{chat_id}.json"
        if not chat_file.exists():
            return []
            
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load messages for {chat_id}: {e}")
            return []

    def save_messages(self, chat_id: str, messages: List[Dict]):
        """Save messages for a chat"""
        chat_file = self.chats_dir / f"{chat_id}.json"
        try:
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2)
                
            # Update 'updated_at' in metadata
            self._update_timestamp(chat_id)
            
        except Exception as e:
            logger.error(f"Failed to save messages for {chat_id}: {e}")

    def update_title(self, chat_id: str, new_title: str):
        """Update the title of a chat"""
        metadata = self._load_metadata()
        for chat in metadata:
            if chat["id"] == chat_id:
                chat["title"] = new_title
                break
        self._save_metadata(metadata)

    def delete_chat(self, chat_id: str):
        """Delete a chat session"""
        # Remove file
        chat_file = self.chats_dir / f"{chat_id}.json"
        if chat_file.exists():
            chat_file.unlink()
            
        # Remove from metadata
        metadata = self._load_metadata()
        metadata = [c for c in metadata if c["id"] != chat_id]
        self._save_metadata(metadata)

    def _update_timestamp(self, chat_id: str):
        """Update the updated_at timestamp in metadata"""
        metadata = self._load_metadata()
        for chat in metadata:
            if chat["id"] == chat_id:
                chat["updated_at"] = datetime.now().isoformat()
                # Move to top? strictly cronological or last active? 
                # Let's keep position for now, or move to top could be nice.
                # Common behavior is move to top.
                metadata.remove(chat)
                metadata.insert(0, chat)
                break
        self._save_metadata(metadata)

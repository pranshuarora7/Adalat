import json
from pathlib import Path
import uuid
from datetime import datetime

class ChatHistory:
    def __init__(self):
        self.chats_dir = Path('data/chats')
        self.chats_dir.mkdir(parents=True, exist_ok=True)

    def save_chat(self, chat_data):
        """Save chat conversation to file"""
        chat_id = chat_data.get('chat_id', str(uuid.uuid4()))
        filename = self.chats_dir / f"{chat_id}.json"
        
        # Add timestamp if not present
        if 'timestamp' not in chat_data:
            chat_data['timestamp'] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(chat_data, f, indent=2)
        
        return chat_id

    def load_chat(self, chat_id):
        """Load chat conversation from file"""
        filename = self.chats_dir / f"{chat_id}.json"
        
        if not filename.exists():
            raise FileNotFoundError(f"Chat {chat_id} not found")
        
        with open(filename, 'r') as f:
            return json.load(f)

    def list_chats(self):
        """List all saved chats"""
        chats = []
        for file in self.chats_dir.glob('*.json'):
            with open(file, 'r') as f:
                chat_data = json.load(f)
                chats.append({
                    'chat_id': file.stem,
                    'timestamp': chat_data.get('timestamp'),
                    'title': chat_data.get('title', 'Untitled Chat')
                })
        
        # Sort by timestamp (newest first)
        chats.sort(key=lambda x: x['timestamp'], reverse=True)
        return chats

# Global instance
chat_history = ChatHistory()

def save_chat_history(chat_data):
    """Wrapper function to save chat history"""
    return chat_history.save_chat(chat_data)

def load_chat_history(chat_id):
    """Wrapper function to load chat history"""
    return chat_history.load_chat(chat_id)

def list_chat_histories():
    """Wrapper function to list all chat histories"""
    return chat_history.list_chats() 
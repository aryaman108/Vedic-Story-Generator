from database import db
from datetime import datetime
import json

class Story(db.Model):
    __tablename__ = 'story'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    prompt_hash = db.Column(db.String(32), index=True)  # For caching
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)  # JSON string of image paths
    audio_path = db.Column(db.String(500))
    video_path = db.Column(db.String(500))
    characters = db.Column(db.Text)  # JSON string of characters
    moral = db.Column(db.Text)  # Moral lesson of the story
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_images(self):
        """Get list of image paths from JSON string"""
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []
        return []
    
    def set_images(self, image_list):
        """Set images as JSON string"""
        self.images = json.dumps(image_list)

    def get_characters(self):
        """Get list of characters from JSON string"""
        if self.characters:
            try:
                return json.loads(self.characters)
            except:
                return []
        return []

    def set_characters(self, character_list):
        """Set characters as JSON string"""
        self.characters = json.dumps(character_list)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'prompt': self.prompt,
            'content': self.content,
            'images': self.get_images(),
            'characters': self.get_characters(),
            'moral': self.moral,
            'audio_path': self.audio_path,
            'video_path': self.video_path,
            'created_at': self.created_at.isoformat()
        }

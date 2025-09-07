from app import db
from datetime import datetime
import json

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)  # JSON string of image paths
    audio_path = db.Column(db.String(500))
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'prompt': self.prompt,
            'content': self.content,
            'images': self.get_images(),
            'audio_path': self.audio_path,
            'created_at': self.created_at.isoformat()
        }

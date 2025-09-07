import os
import logging
from gtts import gTTS
import uuid

def generate_audio_narration(story_content, story_id):
    """Generate audio narration for the story using gTTS"""
    try:
        # Ensure audio directory exists
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        # Clean the text for better speech
        clean_text = clean_text_for_speech(story_content)
        
        # Generate audio using gTTS
        tts = gTTS(text=clean_text, lang='en', slow=False)
        
        # Save audio file
        filename = f"story_{story_id}_narration.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        tts.save(filepath)
        
        logging.info(f"Generated audio: {filename}")
        return f"/static/audio/{filename}"
        
    except Exception as e:
        logging.error(f"Audio generation failed: {e}")
        return None

def clean_text_for_speech(text):
    """Clean text to make it more suitable for speech synthesis"""
    # Remove excessive formatting
    text = text.replace('\n\n', '. ')
    text = text.replace('\n', ' ')
    
    # Handle common Sanskrit terms pronunciation
    replacements = {
        'Krishna': 'Krish-na',
        'Arjuna': 'Ar-ju-na',
        'Dharma': 'Dhar-ma',
        'Karma': 'Kar-ma',
        'Brahma': 'Brah-ma',
        'Vishnu': 'Vish-nu',
        'Shiva': 'Shi-va',
        'Rama': 'Ra-ma',
        'Sita': 'See-ta',
        'Hanuman': 'Ha-nu-man',
        'Mahabharata': 'Ma-ha-bha-ra-ta',
        'Ramayana': 'Ra-ma-ya-na'
    }
    
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    
    # Ensure proper sentence endings
    text = text.replace('..', '.')
    text = text.replace('?.', '?')
    text = text.replace('!.', '!')
    
    return text

def generate_audio_segment(text_segment, segment_id):
    """Generate audio for a specific text segment"""
    try:
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        clean_text = clean_text_for_speech(text_segment)
        tts = gTTS(text=clean_text, lang='en', slow=False)
        
        filename = f"segment_{segment_id}_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        tts.save(filepath)
        return f"/static/audio/{filename}"
        
    except Exception as e:
        logging.error(f"Audio segment generation failed: {e}")
        return None

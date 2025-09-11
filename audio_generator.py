import os
import logging
from gtts import gTTS

def generate_audio_narration(story_content, story_id):
    """Generate audio narration for the story using gTTS"""
    try:
        # Ensure audio directory exists - use Mythoscribe/static path
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)

        # Generate audio using gTTS
        # Truncate content if too long to avoid gTTS limitations
        max_chars = 4000  # gTTS has limitations on text length
        if len(story_content) > max_chars:
            story_content = story_content[:max_chars]
            logging.info(f"Truncated story content to {max_chars} characters for audio generation")
        
        tts = gTTS(text=story_content, lang='en', slow=False, lang_check=False)
        
        # Save audio file
        filename = f"story_{story_id}_narration.mp3"
        filepath = os.path.join(audio_dir, filename)
        
        tts.save(filepath)
        logging.info(f"Generated audio: {filename}")
        
        # Verify file was created
        if os.path.exists(filepath):
            logging.info(f"Audio file exists at: {filepath}")
            # Return the web-accessible path
            return f"/static/audio/{filename}"
        else:
            logging.error(f"Audio file was not created at: {filepath}")
            return None

    except Exception as e:
        logging.error(f"Audio generation failed: {e}")
        return None
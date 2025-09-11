"""
Story Service - Handles the complete story generation workflow
"""

import json
import logging
from database import db
from models import Story
from vedic_story_generator import generate_vedic_story, generate_story_images
from audio_generator import generate_audio_narration
from video_generator import generate_story_video_from_paths

logger = logging.getLogger(__name__)

def create_story_from_prompt(prompt):
    """
    Complete story creation workflow:
    1. Check cache for existing story
    2. Generate story content if not cached
    3. Create database record
    4. Generate images
    5. Generate audio
    6. Generate video
    7. Update database record

    Returns: (story, error_message)
    """
    try:
        logger.info(f"Starting story creation for prompt: {prompt}")

        # Step 1: Check for existing story with same prompt (caching)
        import hashlib
        prompt_hash = hashlib.md5(prompt.strip().lower().encode()).hexdigest()
        existing_story = Story.query.filter_by(prompt_hash=prompt_hash).first()

        if existing_story:
            logger.info(f"Found cached story with ID: {existing_story.id}")
            return existing_story, None

        # Step 2: Generate the story content
        story_data = generate_vedic_story(prompt)
        if not story_data:
            return None, "Failed to generate story"

        # Check if story_data contains an error
        if isinstance(story_data, dict) and 'error' in story_data:
            error_type = story_data.get('type', 'unknown')
            error_message = story_data['error']

            # Provide specific error messages based on error type
            if error_type == 'quota_exceeded':
                return None, 'AI Service Quota Exceeded: The AI service has reached its daily limit. Please try again tomorrow or upgrade your plan.'
            elif error_type == 'permission_denied':
                return None, 'AI Service Access Denied: There\'s an issue with the AI service configuration. Please contact support.'
            elif error_type == 'timeout':
                return None, 'AI Service Timeout: The AI service took too long to respond. Please try again.'
            else:
                return None, f'AI Service Error: {error_message}'

        # Step 3: Create new story record
        story = Story()
        story.title = story_data['title']
        story.prompt = prompt
        story.prompt_hash = prompt_hash  # Add hash for caching
        story.content = story_data['content']
        story.characters = json.dumps(story_data.get('characters', []))
        story.moral = story_data.get('moral', '')

        db.session.add(story)
        db.session.commit()
        logger.info(f"Created story record with ID: {story.id}")

        # Step 3: Generate images for the story
        try:
            image_paths = generate_story_images(story_data, story.id)
            story.set_images(image_paths)
            logger.info(f"Generated {len(image_paths)} images for story {story.id}")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            story.set_images([])

        # Step 4: Generate audio narration
        try:
            audio_path = generate_audio_narration(story_data['content'], story.id)
            story.audio_path = audio_path
            logger.info(f"Generated audio narration for story {story.id}")
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            story.audio_path = None

        # Step 5: Generate video if we have both image and audio
        if image_paths and audio_path:
            try:
                # Use all images for the video sequence
                video_path = generate_story_video_from_paths(
                    image_paths,  # Pass all image paths
                    audio_path,
                    story_data['title'],
                    story_data['content'],
                    story.id
                )
                story.video_path = video_path
                logger.info(f"Generated video sequence for story {story.id}: {video_path}")
            except Exception as e:
                logger.error(f"Video generation failed: {e}")
                story.video_path = None
        else:
            logger.info(f"No video generated for story {story.id} - missing image or audio")
            story.video_path = None

        # Step 6: Save all updates
        db.session.commit()
        logger.info(f"Successfully completed story creation for ID: {story.id}")

        return story, None

    except Exception as e:
        logger.error(f"Story creation error: {e}")
        db.session.rollback()
        return None, f"An error occurred while generating the story: {str(e)}"

def delete_story_files(story):
    """
    Delete all associated files for a story
    """
    import os

    # Delete associated audio file
    if story.audio_path:
        audio_file_path = story.audio_path.lstrip('/')
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            logger.info(f"Deleted audio file: {audio_file_path}")

    # Delete associated image files
    for image_path in story.get_images():
        image_file_path = image_path.lstrip('/')
        if os.path.exists(image_file_path):
            os.remove(image_file_path)
            logger.info(f"Deleted image file: {image_file_path}")

    # Delete video file
    if story.video_path:
        video_file_path = story.video_path.lstrip('/')
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
            logger.info(f"Deleted video file: {video_file_path}")

def create_story_download_text(story):
    """
    Create downloadable text file content for a story
    """
    import os
    from pathlib import Path

    # Create a text file with the story content
    filename = f"story_{story.id}_{story.title.replace(' ', '_')}.txt"
    filepath = os.path.join('static', 'stories', filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {story.title}\n")
        f.write(f"Prompt: {story.prompt}\n")
        f.write(f"Created: {story.created_at}\n")

        # Add characters if available
        if story.get_characters():
            f.write(f"\nCharacters: {', '.join(story.get_characters())}\n")

        # Add moral if available
        if story.moral:
            f.write(f"\nMoral: {story.moral}\n")

        f.write("\n" + "="*50 + "\n\n")
        f.write(story.content)

    return filepath, filename
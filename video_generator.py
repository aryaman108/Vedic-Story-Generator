import os
import logging

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip
    from moviepy.config import change_settings
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logging.warning("MoviePy not available. Video generation will be disabled.")

# Set ImageMagick path if needed (for Windows)
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def generate_story_video(image_path, audio_path, text_caption, story_id):
    """Generate a video combining image, audio, and text caption"""
    if not MOVIEPY_AVAILABLE:
        logging.warning("MoviePy not available, skipping video generation")
        return None

    try:
        logging.info(f"Starting video generation for story ID: {story_id}")

        # Ensure videos directory exists
        videos_dir = os.path.join('static', 'videos')
        os.makedirs(videos_dir, exist_ok=True)

        # Get audio duration and limit to 2-3 minutes max
        audio_clip = AudioFileClip(audio_path)
        max_duration = 180  # 3 minutes max
        duration = min(audio_clip.duration, max_duration)

        # If audio is longer than max, trim it
        if audio_clip.duration > max_duration:
            audio_clip = audio_clip.subclip(0, max_duration)

        logging.info(f"Video duration will be: {duration} seconds")

        # Create image clip
        image_clip = ImageClip(image_path).set_duration(duration)

        # Try to create text clip for caption with fallback options
        text_clip = None
        try:
            # Limit text length to avoid issues
            short_caption = text_caption[:80] if len(text_caption) > 80 else text_caption

            text_clip = TextClip(
                short_caption,
                fontsize=35,  # Smaller font for better compatibility
                color='white',
                bg_color='rgba(0,0,0,0.7)',  # Semi-transparent background
                size=(700, 60)  # Smaller size
            ).set_position(('center', 'bottom')).set_duration(duration)

            # Composite video with text
            video = CompositeVideoClip([image_clip, text_clip])
            logging.info("Video created with text overlay")
        except Exception as text_error:
            logging.warning(f"Text overlay failed, creating video without text: {str(text_error)}")
            # Create video without text overlay
            video = image_clip
            logging.info("Video created without text overlay")
        video = video.set_audio(audio_clip)

        # Export video
        filename = f"story_{story_id}_video.mp4"
        filepath = os.path.join(videos_dir, filename)

        # Write video file with optimized settings for speed and smaller files
        video.write_videofile(
            filepath,
            fps=20,  # Reduced from 30 for faster processing
            codec='libx264',
            audio_codec='aac',
            bitrate='800k',  # Lower bitrate for smaller files
            preset='fast',  # Faster encoding
            temp_audiofile=os.path.join(videos_dir, f"temp_audio_{story_id}.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None,
            threads=2  # Use multiple threads for faster encoding
        )

        # Clean up
        audio_clip.close()
        image_clip.close()
        video.close()
        # Close text_clip if it was created
        if text_clip is not None:
            text_clip.close()

        web_path = f"/static/videos/{filename}"
        logging.info(f"Successfully generated video: {filepath}")
        return web_path

    except Exception as e:
        logging.error(f"Video generation failed: {str(e)}", exc_info=True)
        return None

def generate_story_video_from_paths(image_path, audio_path, story_title, story_content, story_id):
    """Generate video using file paths and story data"""
    try:
        # Convert web paths to file system paths
        if image_path.startswith('/'):
            image_fs_path = image_path.lstrip('/')
        else:
            image_fs_path = image_path

        if audio_path.startswith('/'):
            audio_fs_path = audio_path.lstrip('/')
        else:
            audio_fs_path = audio_path

        # Create caption text (title + short content preview)
        caption_text = story_title
        if len(story_content) > 100:
            caption_text += "\n" + story_content[:100] + "..."
        else:
            caption_text += "\n" + story_content

        return generate_story_video(image_fs_path, audio_fs_path, caption_text, story_id)

    except Exception as e:
        logging.error(f"Video generation from paths failed: {str(e)}", exc_info=True)
        return None
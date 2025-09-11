#!/usr/bin/env python3
"""
Script to regenerate videos for existing stories using the new sequence feature
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Story
from video_generator import generate_story_video_from_paths

def regenerate_videos():
    """Regenerate videos for all existing stories that have images and audio"""
    with app.app_context():
        try:
            # Get all stories that have both images and audio
            stories = Story.query.filter(
                Story.images.isnot(None),
                Story.audio_path.isnot(None)
            ).all()

            print(f"Found {len(stories)} stories with images and audio")

            for story in stories:
                try:
                    print(f"\nProcessing story ID {story.id}: {story.title}")

                    # Get image paths
                    image_paths = story.get_images()
                    if not image_paths:
                        print(f"  No images found for story {story.id}")
                        continue

                    print(f"  Found {len(image_paths)} images")

                    # Regenerate video with sequence
                    video_path = generate_story_video_from_paths(
                        image_paths,
                        story.audio_path,
                        story.title,
                        story.content,
                        story.id
                    )

                    if video_path:
                        story.video_path = video_path
                        db.session.commit()
                        print(f"  ✅ Successfully regenerated video: {video_path}")
                    else:
                        print(f"  ❌ Failed to regenerate video for story {story.id}")

                except Exception as e:
                    print(f"  ❌ Error processing story {story.id}: {str(e)}")
                    continue

            print(f"\n🎬 Video regeneration completed!")

        except Exception as e:
            print(f"❌ Error during video regeneration: {str(e)}")

if __name__ == "__main__":
    regenerate_videos()
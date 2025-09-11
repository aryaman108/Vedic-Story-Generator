#!/usr/bin/env python3
"""
Script to regenerate missing images for stories that have fewer than 4 images
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Story
from image_generator import generate_story_images
from video_generator import generate_story_video_from_paths

def regenerate_missing_images():
    """Regenerate missing images for stories with fewer than 4 images"""
    with app.app_context():
        try:
            # Get all stories
            stories = Story.query.all()

            print(f"Found {len(stories)} total stories")

            for story in stories:
                try:
                    print(f"\nProcessing story ID {story.id}: {story.title}")

                    # Get current images
                    current_images = story.get_images()
                    print(f"  Current images: {len(current_images)}")

                    if len(current_images) < 4:
                        print(f"  ERROR: Story {story.id} has only {len(current_images)} images, needs 4")

                        # Regenerate all images for this story
                        # First, let's try to get the story data to regenerate images
                        # Since we don't have the original story data, we'll need to recreate it

                        # For now, let's create placeholder images for missing scenes
                        from image_generator import create_visual_scene_image
                        import json

                        images_dir = os.path.join('static', 'images')
                        os.makedirs(images_dir, exist_ok=True)

                        new_image_paths = []

                        # Keep existing images
                        for i, img_path in enumerate(current_images):
                            if i < 4:  # Only keep up to 4 images
                                new_image_paths.append(img_path)

                        # Generate missing images
                        for i in range(len(current_images), 4):
                            print(f"  Generating missing image {i+1} for story {story.id}")
                            filename = f"story_{story.id}_scene_{i+1}.png"
                            filepath = os.path.join(images_dir, filename)

                            # Create a placeholder image
                            from PIL import Image, ImageDraw, ImageFont
                            width, height = 512, 384
                            image = Image.new('RGB', (width, height), color=(135, 206, 235))
                            draw = ImageDraw.Draw(image)

                            # Simple ground
                            draw.rectangle([0, height//2, width, height], fill=(139, 69, 19))

                            # Simple mountain
                            mountain_points = [(0, height//2), (width//3, height//2 - 60), (2*width//3, height//2 - 40), (width, height//2)]
                            draw.polygon(mountain_points, fill=(101, 67, 33))

                            # Title
                            font = ImageFont.load_default()
                            title = f"Scene {i+1}"
                            title_bbox = draw.textbbox((0, 0), title, font=font)
                            title_width = title_bbox[2] - title_bbox[0]
                            title_x = (width - title_width) // 2
                            draw.text((title_x, 10), title, fill=(0, 0, 0), font=font)

                            # Save the image
                            image.save(filepath)
                            web_path = f"/static/images/{filename}"
                            new_image_paths.append(web_path)
                            print(f"  SUCCESS: Created placeholder image: {filepath}")

                        # Update story with new images
                        story.set_images(new_image_paths)
                        db.session.commit()
                        print(f"  SUCCESS: Updated story {story.id} with {len(new_image_paths)} images")

                        # Regenerate video with all images
                        if story.audio_path:
                            print(f"  Regenerating video for story {story.id}")
                            video_path = generate_story_video_from_paths(
                                new_image_paths,
                                story.audio_path,
                                story.title,
                                story.content,
                                story.id
                            )

                            if video_path:
                                story.video_path = video_path
                                db.session.commit()
                                print(f"  SUCCESS: Successfully regenerated video: {video_path}")
                            else:
                                print(f"  ERROR: Failed to regenerate video for story {story.id}")
                        else:
                            print(f"  WARNING: No audio path for story {story.id}, skipping video generation")

                    else:
                        print(f"  SUCCESS: Story {story.id} already has {len(current_images)} images")

                except Exception as e:
                    print(f"  ERROR: Error processing story {story.id}: {str(e)}")
                    continue

            print(f"\nImage regeneration completed!")

        except Exception as e:
            print(f"ERROR: Error during image regeneration: {str(e)}")

if __name__ == "__main__":
    regenerate_missing_images()
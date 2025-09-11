import os
import json
import logging
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv
import random

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

def generate_story_images(story_data, story_id):
    """
    Generate images for story scenes using AI image generation services.

    This function handles the complete image generation pipeline:
    1. Validates and prepares the images directory
    2. Processes each scene from the story data
    3. Generates images using Pollinations AI as primary service
    4. Falls back to placeholder generation if AI fails
    5. Returns web-accessible paths for all generated images

    Args:
        story_data (dict): Story data containing scenes and metadata
        story_id (int): Unique identifier for the story

    Returns:
        list: List of web paths to generated images (/static/images/filename.png)
    """
    try:
        logger.info(f"Starting image generation for story ID: {story_id}")

        # Ensure images directory exists - use Mythoscribe/static path
        images_dir = os.path.join('static', 'images')
        os.makedirs(images_dir, exist_ok=True)

        image_paths = []
        scenes = story_data.get('scenes', [])

        # Handle case where no scenes are provided in story data
        if not scenes:
            logger.warning("No scenes found in story data, creating placeholder images")
            # Create 4 placeholder images for consistent video sequences
            for i in range(4):
                style = "traditional Indian miniature art"
                create_visual_scene_image(images_dir, story_id, i, style, f"Scene {i+1} placeholder", image_paths)
            return image_paths

        if not scenes:
            logger.warning("No scenes found in story data, creating placeholder images")
            # Create placeholder images if no scenes
            for i in range(4):
                style = "traditional Indian miniature art"
                create_visual_scene_image(images_dir, story_id, i, style, f"Scene {i+1} placeholder", image_paths)
            return image_paths

        styles = [
            "traditional Indian miniature art (Pahari/Kangra/Rajput style)",
            "Kerala mural painting style",
            "Tanjore painting style with gold leaf detailing",
            "Mysore painting style",
            "Pattachitra style from Odisha"
        ]

        # Generate exactly 4 images for consistent video sequences
        # Pre-select random styles to avoid repeated random.choice calls
        selected_styles = random.choices(styles, k=4)
        num_scenes = len(scenes)

        for i in range(4):
            if i < num_scenes:
                scene = scenes[i]
            else:
                # Create a placeholder scene if we don't have enough scenes
                scene = f"Scene {i+1}: Continuation of the Vedic story '{story_data.get('title', 'Story')}' - depicting divine characters and sacred elements in traditional Indian art style"
            try:
                logger.info(f"Generating image {i+1} for scene: {scene[:100]}...")

                style = selected_styles[i]  # Use pre-selected style for better performance
                # Create detailed prompt for image generation with user context
                image_prompt = f"""Create a masterpiece digital painting in the style of {style} depicting: {scene}

                ARTISTIC STYLE: {style} with exceptional detail and craftsmanship
                QUALITY: Ultra-high resolution, professional illustration quality, photorealistic details
                COLORS: Rich, vibrant Vedic color palette with gold, saffron, deep blues, and traditional hues
                LIGHTING: Divine golden glow, spiritual atmosphere with ethereal light
                COMPOSITION: Balanced, harmonious layout with proper perspective and depth

                AUTHENTIC ELEMENTS TO INCLUDE:
                - Traditional Indian/Vedic iconography and sacred symbols
                - Authentic period-appropriate clothing and jewelry
                - Divine attributes, mudras (hand gestures), and expressions
                - Sacred geometry, yantras, and traditional decorative elements
                - Cultural accuracy in architecture, objects, and settings

                TECHNICAL EXCELLENCE:
                - Sharp, crisp details with no blurring
                - Professional color grading and contrast
                - High dynamic range with proper shadows and highlights
                - Traditional artistic techniques with modern digital quality

                CONTEXT: This illustration is for a Vedic mythological story - ensure all elements are culturally and spiritually accurate."""

                # Use Google Gemini for high-quality image generation
                try:
                    logger.info(f"Generating image using Gemini API for scene: {scene[:100]}...")

                    # Create detailed prompt for Gemini image generation with user context
                    gemini_prompt = f"""Create a masterpiece digital painting depicting: {scene}

ARTISTIC STYLE: {style} with exceptional detail and craftsmanship
QUALITY: Ultra-high resolution, professional illustration quality, photorealistic details
COLORS: Rich, vibrant Vedic color palette with gold, saffron, deep blues, and traditional hues
LIGHTING: Divine golden glow, spiritual atmosphere with ethereal light
COMPOSITION: Balanced, harmonious layout with proper perspective and depth

AUTHENTIC ELEMENTS TO INCLUDE:
- Traditional Indian/Vedic iconography and sacred symbols
- Authentic period-appropriate clothing and jewelry
- Divine attributes, mudras (hand gestures), and expressions
- Sacred geometry, yantras, and traditional decorative elements
- Cultural accuracy in architecture, objects, and settings

TECHNICAL EXCELLENCE:
- Sharp, crisp details with no blurring
- Professional color grading and contrast
- High dynamic range with proper shadows and highlights
- Traditional artistic techniques with modern digital quality

CONTEXT: This illustration is for a Vedic mythological story - ensure all elements are culturally and spiritually accurate.

Make this a complete visual scene that tells the story, not just text or descriptions."""

                    # Use Pollinations AI for image generation (Gemini image generation not available)
                    logger.info("Using Pollinations AI for image generation...")

                    # Create optimized prompt for Pollinations AI
                    visual_prompt = f"Indian mythology {scene[:50]} traditional art colorful divine"
                    encoded_prompt = visual_prompt.replace(' ', '%20').replace(',', '%2C')
                    API_URL = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=384&nologo=true&model=flux"

                    try:
                        response = requests.get(API_URL, timeout=30)  # Reduced timeout

                        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                            filename = f"story_{story_id}_scene_{i+1}.png"
                            filepath = os.path.join(images_dir, filename)

                            with open(filepath, "wb") as f:
                                f.write(response.content)

                            web_path = f"/static/images/{filename}"
                            image_paths.append(web_path)
                            logger.info(f"Successfully generated image with Pollinations AI: {filepath}")
                        else:
                            logger.warning(f"Pollinations AI failed with status {response.status_code}, creating visual placeholder")
                            create_visual_scene_image(images_dir, story_id, i, style, scene, image_paths)
                    except Exception as poll_error:
                        logger.warning(f"Pollinations AI request failed: {str(poll_error)}, creating visual placeholder")
                        create_visual_scene_image(images_dir, story_id, i, style, scene, image_paths)

                except Exception as e:
                    logger.error(f"Error with image generation: {str(e)}")
                    create_visual_scene_image(images_dir, story_id, i, style, scene, image_paths)

            except Exception as e:
                logger.error(f"Error generating placeholder image {i+1}: {str(e)}", exc_info=True)
                continue

        logger.info(f"Image generation completed for story {story_id}, generated {len(image_paths)} images")
        return image_paths

    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}", exc_info=True)
        return []

def create_visual_scene_image(images_dir, story_id, index, style, scene, image_paths):
    """Create simplified visual scene representation"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create simple canvas with gradient background
        width, height = 512, 384  # Smaller size for faster generation
        image = Image.new('RGB', (width, height), color=(135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(image)

        # Simple ground
        draw.rectangle([0, height//2, width, height], fill=(139, 69, 19))

        # Simple mountain
        mountain_points = [(0, height//2), (width//3, height//2 - 60), (2*width//3, height//2 - 40), (width, height//2)]
        draw.polygon(mountain_points, fill=(101, 67, 33))

        # Simple tree
        tree_x = width//4
        draw.rectangle([tree_x-3, height//2, tree_x+3, height//2 + 30], fill=(101, 67, 33))
        draw.ellipse([tree_x-15, height//2 - 15, tree_x+15, height//2 + 15], fill=(34, 139, 34))

        # Simple figure based on scene
        if any(keyword in scene.lower() for keyword in ['hanuman', 'monkey', 'vanara']):
            figure_x, figure_y = width//2, height//2 + 20
            draw.ellipse([figure_x-10, figure_y, figure_x+10, figure_y+40], fill=(255, 140, 0))
            draw.ellipse([figure_x-8, figure_y-15, figure_x+8, figure_y+5], fill=(255, 140, 0))
        elif any(keyword in scene.lower() for keyword in ['krishna', 'rama', 'lord']):
            figure_x, figure_y = width//2, height//2 + 20
            color = (0, 100, 200) if 'krishna' in scene.lower() else (255, 215, 0)
            draw.ellipse([figure_x-8, figure_y, figure_x+8, figure_y+35], fill=color)
            draw.ellipse([figure_x-6, figure_y-12, figure_x+6, figure_y+3], fill=(255, 220, 177))

        # Simple sun
        draw.ellipse([width-60, 20, width-20, 60], fill=(255, 255, 0))

        # Title
        font = ImageFont.load_default()
        title = f"Scene {index+1}"
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 10), title, fill=(0, 0, 0), font=font)

        # Save the image
        filename = f"story_{story_id}_scene_{index+1}.png"
        filepath = os.path.join(images_dir, filename)
        image.save(filepath)
        web_path = f"/static/images/{filename}"
        image_paths.append(web_path)
        logging.info(f"Created simplified visual scene image: {filepath}")

    except Exception as e:
        logging.error(f"Error creating visual scene image: {str(e)}", exc_info=True)
        create_simple_placeholder_image(images_dir, story_id, index, style, scene, image_paths)

def create_simple_placeholder_image(images_dir, story_id, index, style, scene, image_paths):
    """Simple fallback placeholder"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        width, height = 800, 600
        image = Image.new('RGB', (width, height), color=(101, 67, 33))  # Brown
        draw = ImageDraw.Draw(image)

        # Simple text
        font = ImageFont.load_default()
        text = f"Story Illustration {index+1}\n{style.split('(')[0].strip()}"
        draw.text((50, height//2), text, fill=(255, 255, 255), font=font)

        filename = f"story_{story_id}_scene_{index+1}.png"
        filepath = os.path.join(images_dir, filename)

        image.save(filepath)
        web_path = f"/static/images/{filename}"
        image_paths.append(web_path)
        logging.info(f"Created simple placeholder: {filepath}")

    except Exception as e:
        logging.error(f"Error creating simple placeholder: {str(e)}")
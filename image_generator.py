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
    """Generate images for story scenes using a free image generation service"""
    try:
        logger.info(f"Starting image generation for story ID: {story_id}")

        # Ensure images directory exists - use Mythoscribe/static path
        images_dir = os.path.join('static', 'images')
        os.makedirs(images_dir, exist_ok=True)

        image_paths = []
        scenes = story_data.get('scenes', [])

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

        # Generate up to 4 images for better story coverage
        for i, scene in enumerate(scenes[:4]):
            try:
                logger.info(f"Generating image {i+1} for scene: {scene[:100]}...")

                style = random.choice(styles)
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

                    # Create prompt for Pollinations AI
                    visual_prompt = f"Indian mythology, {scene.split(',')[0]}, traditional art style, colorful, detailed characters, divine setting"
                    encoded_prompt = visual_prompt.replace(' ', '%20').replace(',', '%2C')
                    API_URL = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true&model=flux"

                    try:
                        response = requests.get(API_URL, timeout=60)

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
    """Create actual visual scene representation instead of text"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random
        import math

        # Create canvas
        width, height = 800, 600

        # Create sky gradient background
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        # Sky gradient (blue to orange/pink)
        for y in range(height//2):
            ratio = y / (height//2)
            r = int(135 + ratio * 120)  # Blue to orange
            g = int(206 + ratio * 49)   # Light blue to yellow
            b = int(235 - ratio * 135)  # Light blue to orange
            color = (min(255, r), min(255, g), max(100, b))
            draw.line([(0, y), (width, y)], fill=color)

        # Ground (earth tones)
        for y in range(height//2, height):
            ratio = (y - height//2) / (height//2)
            r = int(139 - ratio * 40)  # Brown tones
            g = int(69 + ratio * 30)
            b = int(19 + ratio * 20)
            color = (max(50, r), max(30, g), max(10, b))
            draw.line([(0, y), (width, y)], fill=color)

        # Draw mountains in background
        mountain_points = [
            (0, height//2), (150, height//2 - 100), (300, height//2 - 80),
            (450, height//2 - 120), (600, height//2 - 60), (width, height//2 - 40), (width, height//2), (0, height//2)
        ]
        draw.polygon(mountain_points, fill=(101, 67, 33), outline=(139, 69, 19))

        # Draw trees
        tree_positions = [(100, height//2), (200, height//2 + 20), (600, height//2 + 10), (700, height//2 - 10)]
        for tree_x, tree_y in tree_positions:
            # Tree trunk
            draw.rectangle([tree_x-5, tree_y, tree_x+5, tree_y+40], fill=(101, 67, 33))
            # Tree foliage
            draw.ellipse([tree_x-20, tree_y-20, tree_x+20, tree_y+10], fill=(34, 139, 34))

        # Draw figures based on scene content
        if any(keyword in scene.lower() for keyword in ['hanuman', 'monkey', 'vanara']):
            # Draw Hanuman figure
            hanuman_x, hanuman_y = width//2, height//2 + 50
            # Body
            draw.ellipse([hanuman_x-15, hanuman_y, hanuman_x+15, hanuman_y+60], fill=(255, 140, 0))  # Orange
            # Head
            draw.ellipse([hanuman_x-12, hanuman_y-25, hanuman_x+12, hanuman_y+5], fill=(255, 140, 0))
            # Tail
            draw.ellipse([hanuman_x+15, hanuman_y+30, hanuman_x+35, hanuman_y+40], fill=(255, 140, 0))

        elif any(keyword in scene.lower() for keyword in ['krishna', 'rama', 'lord']):
            # Draw divine figure
            figure_x, figure_y = width//2, height//2 + 50
            # Body (blue for Krishna, golden for others)
            color = (0, 100, 200) if 'krishna' in scene.lower() else (255, 215, 0)
            draw.ellipse([figure_x-12, figure_y, figure_x+12, figure_y+50], fill=color)
            # Head
            draw.ellipse([figure_x-10, figure_y-20, figure_x+10, figure_y], fill=(255, 220, 177))  # Skin tone
            # Crown/halo
            draw.ellipse([figure_x-15, figure_y-25, figure_x+15, figure_y-15], fill=(255, 215, 0), outline=(255, 140, 0))

        # Draw objects based on scene
        if 'mountain' in scene.lower():
            # Draw mountain being lifted
            mountain_x = width//2 + 100
            mountain_points = [
                (mountain_x-40, height//2), (mountain_x, height//2 - 60),
                (mountain_x+40, height//2), (mountain_x-40, height//2)
            ]
            draw.polygon(mountain_points, fill=(105, 105, 105), outline=(169, 169, 169))

        if 'temple' in scene.lower() or 'palace' in scene.lower():
            # Draw temple structure
            temple_x, temple_y = width//2 + 150, height//2
            draw.rectangle([temple_x-30, temple_y, temple_x+30, temple_y+80], fill=(139, 69, 19))
            # Temple top
            temple_top = [(temple_x-35, temple_y), (temple_x, temple_y-30), (temple_x+35, temple_y)]
            draw.polygon(temple_top, fill=(255, 215, 0))

        # Add divine elements
        # Draw sun/divine light
        sun_x, sun_y = width - 100, 80
        draw.ellipse([sun_x-30, sun_y-30, sun_x+30, sun_y+30], fill=(255, 255, 0), outline=(255, 140, 0))

        # Draw rays
        for angle in range(0, 360, 45):
            end_x = sun_x + 50 * math.cos(math.radians(angle))
            end_y = sun_y + 50 * math.sin(math.radians(angle))
            draw.line([sun_x, sun_y, end_x, end_y], fill=(255, 215, 0), width=2)

        # Add flowers/lotus
        flower_positions = [(150, height-100), (650, height-80)]
        for fx, fy in flower_positions:
            draw.ellipse([fx-8, fy-8, fx+8, fy+8], fill=(255, 20, 147))  # Pink flower
            for petal in range(6):
                angle = petal * 60
                px = fx + 12 * math.cos(math.radians(angle))
                py = fy + 12 * math.sin(math.radians(angle))
                draw.ellipse([px-4, py-4, px+4, py+4], fill=(255, 182, 193))

        # Add title only (no description text)
        font = ImageFont.load_default()
        title = f"Scene {index+1}"
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2

        # Title with background
        draw.rectangle([title_x-10, 20, title_x+title_width+10, 50], fill=(0, 0, 0, 128), outline=(255, 215, 0))
        draw.text((title_x, 30), title, fill=(255, 255, 255), font=font)

        # Save the visual scene
        filename = f"story_{story_id}_scene_{index+1}.png"
        filepath = os.path.join(images_dir, filename)

        image.save(filepath)
        web_path = f"/static/images/{filename}"
        image_paths.append(web_path)
        logging.info(f"Created visual scene image: {filepath}")

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
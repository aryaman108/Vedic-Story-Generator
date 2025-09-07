import os
import logging
import requests
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_story_images(story_data, story_id):
    """Generate images for story scenes using DALL-E"""
    try:
        # Ensure images directory exists
        images_dir = os.path.join('static', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        image_paths = []
        scenes = story_data.get('scenes', [])
        
        # Limit to 3 images to avoid excessive API usage
        for i, scene in enumerate(scenes[:3]):
            try:
                # Create detailed prompt for DALL-E
                image_prompt = f"""Create a beautiful, artistic illustration in the style of traditional Indian miniature paintings depicting: {scene}

Style: Traditional Indian art, rich colors, detailed patterns, mythological theme, spiritual atmosphere, ornate decorations, golden accents.

Focus on authenticity to Vedic Hindu traditions and mythology."""

                response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    quality="standard"
                )
                
                if not response.data or len(response.data) == 0:
                    raise ValueError("No image data received from OpenAI")
                image_url = response.data[0].url
                
                # Download and save the image
                if not image_url:
                    raise ValueError("No image URL received")
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    filename = f"story_{story_id}_scene_{i+1}.png"
                    filepath = os.path.join(images_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    image_paths.append(f"/static/images/{filename}")
                    logging.info(f"Generated image: {filename}")
                
            except Exception as e:
                logging.error(f"Failed to generate image {i+1}: {e}")
                continue
        
        return image_paths
        
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        return []

def generate_character_image(character_description):
    """Generate an image of a specific character"""
    try:
        image_prompt = f"""Create a detailed portrait in traditional Indian miniature painting style: {character_description}

Style: Classical Indian art, vibrant colors, ornate clothing, divine attributes, spiritual aura, intricate jewelry, traditional pose.

Make it authentic to Vedic Hindu iconography and mythology."""

        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )
        
        if not response.data or len(response.data) == 0:
            raise ValueError("No image data received from OpenAI")
        return response.data[0].url
        
    except Exception as e:
        logging.error(f"Character image generation failed: {e}")
        return None

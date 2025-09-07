import os
import logging
import requests
import fal_client

FAL_KEY = os.environ.get("FAL_KEY")
if FAL_KEY:
    os.environ["FAL_KEY"] = FAL_KEY

def generate_story_images(story_data, story_id):
    """Generate images for story scenes using Flux AI"""
    try:
        # Check if FAL_KEY is available
        if not os.environ.get("FAL_KEY"):
            logging.warning("FAL_KEY not found, skipping image generation")
            return []
            
        # Ensure images directory exists
        images_dir = os.path.join('static', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        image_paths = []
        scenes = story_data.get('scenes', [])
        
        # Limit to 3 images to avoid excessive API usage
        for i, scene in enumerate(scenes[:3]):
            try:
                # Create detailed prompt for Flux
                image_prompt = f"""Create a beautiful, artistic illustration in the style of traditional Indian miniature paintings depicting: {scene}

Style: Traditional Indian art, rich vibrant colors, detailed patterns, mythological theme, spiritual atmosphere, ornate decorations, golden accents, divine aura.

Focus on authenticity to Vedic Hindu traditions and mythology. High quality, detailed artwork."""

                # Use Flux Schnell for fast generation
                result = fal_client.subscribe("fal-ai/flux/schnell", {
                    "prompt": image_prompt,
                    "image_size": "landscape_4_3",
                    "num_inference_steps": 4,
                    "num_images": 1,
                    "enable_safety_checker": True
                })
                
                if not result or not result.get('images') or len(result['images']) == 0:
                    raise ValueError("No image data received from Flux")
                image_url = result['images'][0]['url']
                
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
                    logging.info(f"Generated Flux image: {filename}")
                
            except Exception as e:
                logging.error(f"Failed to generate Flux image {i+1}: {e}")
                continue
        
        return image_paths
        
    except Exception as e:
        logging.error(f"Flux image generation failed: {e}")
        return []

def generate_character_image(character_description):
    """Generate an image of a specific character using Flux AI"""
    try:
        # Check if FAL_KEY is available
        if not os.environ.get("FAL_KEY"):
            logging.warning("FAL_KEY not found, skipping character image generation")
            return None
            
        image_prompt = f"""Create a detailed portrait in traditional Indian miniature painting style: {character_description}

Style: Classical Indian art, vibrant colors, ornate clothing, divine attributes, spiritual aura, intricate jewelry, traditional pose.

Make it authentic to Vedic Hindu iconography and mythology. High quality, detailed artwork."""

        # Use Flux Schnell for fast generation
        result = fal_client.subscribe("fal-ai/flux/schnell", {
            "prompt": image_prompt,
            "image_size": "square",
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": True
        })
        
        if not result or not result.get('images') or len(result['images']) == 0:
            raise ValueError("No image data received from Flux")
        return result['images'][0]['url']
        
    except Exception as e:
        logging.error(f"Flux character image generation failed: {e}")
        return None

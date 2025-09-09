import os
import json
import logging
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    logger.info("Loaded .env file")

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model with the correct model name
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_vedic_story(prompt):
    """Generate a Vedic mythology story using Gemini Pro"""
    for attempt in range(3):
        try:
            logger.info(f"Generating story for prompt: {prompt} (Attempt {attempt + 1})")

            system_prompt = """You are a master storyteller and scholar of Vedic Hindu dharma. You have encyclopedic knowledge of:
- The four Vedas (Rig, Yajur, Sama, Atharva)
- Major Upanishads and Puranas
- Itihasas (Ramayana, Mahabharata)
- Darshana Shastras and Dharma Shastras

When creating stories, you MUST:
1. Base all characters, events, and teachings on authentic Vedic sources
2. Include specific references (e.g., "As described in the Bhagavata Purana 10.8.3")
3. Maintain consistency with Vedic cosmology and philosophy
4. Include Sanskrit terms with English translations
5. Provide spiritual insights and moral lessons

Format your response as a JSON object with these fields:
{
    "title": "Story Title",
    "content": "Full story content...",
    "scenes": [
        "Detailed visual description of scene 1 for high-quality image generation - include specific colors, lighting, composition, and artistic style",
        "Detailed visual description of scene 2 for high-quality image generation - include specific colors, lighting, composition, and artistic style",
        "Detailed visual description of scene 3 for high-quality image generation - include specific colors, lighting, composition, and artistic style",
        "Detailed visual description of scene 4 for high-quality image generation - include specific colors, lighting, composition, and artistic style"
    ],
    "characters": ["Character 1", "Character 2", ...],
    "moral": "The moral or lesson of the story",
    "sources": ["Reference 1", "Reference 2", ...]
}

IMPORTANT: For the scenes array, provide 4 detailed visual descriptions that capture different key moments of the story. Each scene description should be optimized for AI image generation and include:
- Specific artistic style (traditional Indian painting, miniature art, etc.)
- Detailed character appearances and expressions
- Color palette and lighting
- Composition and perspective
- Cultural and mythological accuracy
- High-quality artistic elements

Make the story engaging, educational, and spiritually uplifting."""

            # Generate the story
            response = model.generate_content(
                f"{system_prompt}\n\nCreate a Vedic story about: {prompt}"
            )

            # Extract the JSON response
            content = response.text.strip()
            logger.debug(f"Raw response from Gemini: {content}")

            # Clean the response to extract just the JSON part
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            # Parse the JSON
            story_data = json.loads(content)
            logger.info(f"Successfully generated story: {story_data.get('title', 'Untitled')}")
            return story_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response on attempt {attempt + 1}: {e}")
            logger.error(f"Response content: {content}")
            if attempt < 2:
                logger.info("Retrying...")
                continue
            else:
                return {"error": "Failed to parse story response from AI", "type": "json_error"}
        except Exception as e:
            error_str = str(e)
            logger.error(f"Story generation failed on attempt {attempt + 1}: {error_str}", exc_info=True)

            # Check for specific error types
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                logger.error("Gemini API quota exceeded")
                return {"error": "AI service quota exceeded. Please try again later or contact support.", "type": "quota_exceeded"}
            elif "403" in error_str or "permission" in error_str.lower():
                logger.error("Gemini API permission denied")
                return {"error": "AI service access denied. Please check API configuration.", "type": "permission_denied"}
            elif "timeout" in error_str.lower() or "deadline" in error_str.lower():
                logger.error("Gemini API timeout")
                if attempt < 2:
                    logger.info("Retrying due to timeout...")
                    continue
                else:
                    return {"error": "AI service timeout. Please try again.", "type": "timeout"}
            else:
                if attempt < 2:
                    logger.info("Retrying due to unknown error...")
                    continue
                else:
                    return {"error": f"AI service error: {error_str}", "type": "unknown_error"}

    # All attempts failed
    return {"error": "Failed to generate story after multiple attempts. Please try again later.", "type": "max_retries_exceeded"}
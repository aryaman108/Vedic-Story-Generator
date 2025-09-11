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
    """
    Generate a Vedic mythology story using Google's Gemini AI model.

    This function implements a robust story generation pipeline with:
    - Retry logic for handling API failures
    - Optimized prompts for faster, more accurate responses
    - Comprehensive error handling for different failure types
    - JSON parsing with fallback error responses

    Args:
        prompt (str): User-provided prompt describing the desired story

    Returns:
        dict: Story data containing title, content, scenes, characters, moral, and sources
              Or error dict with 'error' key and 'type' field for error classification
    """
    # Retry up to 2 times to handle transient API failures
    for attempt in range(2):
        try:
            logger.info(f"Generating story for prompt: {prompt} (Attempt {attempt + 1})")

            # Optimized system prompt for Vedic storytelling - concise yet comprehensive
            # Using f-string for better performance and readability
            system_prompt = (
                "You are a Vedic storyteller. Create authentic Hindu mythology stories with:\n"
                "- Characters and events from Vedas, Puranas, Ramayana, Mahabharata\n"
                "- Sanskrit terms with translations\n"
                "- Spiritual insights and morals\n"
                "- EXACTLY 4 detailed scene descriptions for images (no more, no less)\n\n"
                "Return JSON:\n"
                "{\n"
                '  "title": "Story Title",\n'
                '  "content": "Full story...",\n'
                '  "scenes": ["Scene 1 description", "Scene 2", "Scene 3", "Scene 4"],\n'
                '  "characters": ["Char1", "Char2"],\n'
                '  "moral": "Lesson",\n'
                '  "sources": ["Reference"]\n'
                "}\n\n"
                "CRITICAL: You MUST provide exactly 4 scenes in the scenes array. Each scene should be vivid and detailed for AI image generation with traditional Indian art style."
            )

            # Generate the story with optimized settings
            response = model.generate_content(
                f"{system_prompt}\n\nCreate a Vedic story about: {prompt}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Balanced creativity
                    max_output_tokens=2048,  # Limit output size
                )
            )

            # Extract and clean the JSON response from Gemini
            content = response.text.strip()
            logger.debug(f"Raw response from Gemini: {content}")

            # Handle different markdown code block formats that Gemini might return
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            # Parse the cleaned JSON response
            story_data = json.loads(content)
            logger.info(f"Successfully generated story: {story_data.get('title', 'Untitled')}")
            return story_data

        except json.JSONDecodeError as e:
            # Handle malformed JSON responses from the AI
            logger.error(f"Failed to parse JSON response on attempt {attempt + 1}: {e}")
            logger.error(f"Response content: {content}")
            if attempt < 1:  # Allow retry for first attempt only
                logger.info("Retrying due to JSON parsing error...")
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
                if attempt < 1:  # Updated for 2 attempts
                    logger.info("Retrying due to timeout...")
                    continue
                else:
                    return {"error": "AI service timeout. Please try again.", "type": "timeout"}
            else:
                if attempt < 1:  # Updated for 2 attempts
                    logger.info("Retrying due to unknown error...")
                    continue
                else:
                    return {"error": f"AI service error: {error_str}", "type": "unknown_error"}

    # All attempts failed
    return {"error": "Failed to generate story after multiple attempts. Please try again later.", "type": "max_retries_exceeded"}
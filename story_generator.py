import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_vedic_story(prompt):
    """Generate a Vedic mythology story based on the given prompt"""
    try:
        system_prompt = """You are a master storyteller specializing in Vedic Hindu mythology. You have deep knowledge of the Ramayana, Mahabharata, Puranas, Vedas, and other sacred texts. 

Create engaging, authentic stories that:
- Draw from genuine Vedic traditions and characters
- Include moral lessons and spiritual insights
- Use appropriate Sanskrit terms and names
- Maintain cultural accuracy and respect
- Are suitable for all audiences
- Include vivid descriptions for visualization

Respond with JSON in this exact format:
{
    "title": "Story title",
    "content": "Full story content with multiple paragraphs",
    "scenes": ["Scene 1 description", "Scene 2 description", "Scene 3 description"],
    "characters": ["Character 1", "Character 2", "Character 3"],
    "moral": "Key moral or spiritual lesson"
}"""

        user_prompt = f"""Create a Vedic mythology story based on this prompt: {prompt}

The story should be engaging, authentic to Vedic traditions, and include:
- Rich character development
- Vivid scene descriptions
- Cultural and spiritual elements
- A meaningful conclusion with moral teachings

Make it approximately 800-1200 words long."""

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        story_data = json.loads(content)
        logging.info(f"Generated story: {story_data.get('title', 'Untitled')}")
        
        return story_data
        
    except Exception as e:
        logging.error(f"Story generation failed: {e}")
        return None

def extract_story_scenes(story_content):
    """Extract key scenes from story content for image generation"""
    try:
        system_prompt = """You are an expert at analyzing stories and identifying key visual scenes. 
        
        Analyze the given story and identify 3-4 key scenes that would make compelling images.
        Focus on:
        - Dramatic moments
        - Character interactions
        - Scenic descriptions
        - Symbolic elements
        
        Respond with JSON in this format:
        {
            "scenes": [
                "Detailed scene description 1",
                "Detailed scene description 2", 
                "Detailed scene description 3"
            ]
        }"""
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract key visual scenes from this story:\n\n{story_content}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        scenes_data = json.loads(content)
        return scenes_data.get('scenes', [])
        
    except Exception as e:
        logging.error(f"Scene extraction failed: {e}")
        return []

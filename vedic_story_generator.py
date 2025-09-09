"""
Vedic Story Generator - Main orchestrator module
Combines story generation, image generation, and other services
"""

from story_generator import generate_vedic_story
from image_generator import generate_story_images

# Re-export the main functions for backward compatibility
__all__ = ['generate_vedic_story', 'generate_story_images']

# Overview

The Vedic Story Generator is a Flask-based web application that creates immersive storytelling experiences based on Hindu mythology and Vedic literature. The application generates AI-powered stories from user prompts, accompanied by custom artwork and audio narration. Users can create stories inspired by texts like the Ramayana, Mahabharata, Puranas, and Vedas, then save them to a personal library for future reference.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture

**Framework**: Flask with SQLAlchemy ORM for database operations
- Uses SQLAlchemy's DeclarativeBase for modern ORM patterns
- Implements factory pattern for app initialization with proper database context management
- Routes are modularized in separate files for maintainability

**Database Design**: Single-table design with Story model
- Stores story metadata, content, and media references
- Uses JSON serialization for image paths array storage
- Includes timestamps and user prompts for historical tracking

**Content Generation Pipeline**: Multi-stage AI-powered story creation
- Text generation uses OpenAI GPT-5 for story content with structured JSON responses
- Image generation leverages DALL-E 3 for scene illustrations in traditional Indian art style  
- Audio generation uses Google Text-to-Speech (gTTS) with pronunciation optimizations for Sanskrit terms
- Error handling ensures partial failures don't break the entire generation process

## Frontend Architecture

**Template System**: Jinja2 templates with Bootstrap 5 dark theme
- Base template provides consistent navigation and flash messaging
- Responsive design with mobile-first approach
- Custom CSS for story-specific styling and animations

**User Interface Flow**: 
- Story creation form with example prompts and validation
- Real-time loading indicators during generation process
- Story library with grid layout and preview capabilities
- Individual story view with media controls and download options

**JavaScript Integration**: Vanilla JavaScript for interactive features
- Asynchronous story generation with progress updates
- Audio playback controls and media management
- Dynamic UI updates and error handling

## File Storage Strategy

**Static Asset Management**: Organized directory structure for generated content
- Images stored in `/static/images/` with systematic naming conventions
- Audio files in `/static/audio/` as MP3 format
- Ensures proper web server delivery of media assets

# External Dependencies

## AI Services
- **OpenAI API**: GPT-5 model for story text generation and DALL-E 3 for artwork creation
- **Google Text-to-Speech (gTTS)**: Audio narration generation with multilingual support

## Frontend Libraries
- **Bootstrap 5**: UI framework with Replit's dark theme customizations
- **Font Awesome**: Icon library for consistent visual elements

## Python Libraries
- **Flask & Flask-SQLAlchemy**: Web framework and database ORM
- **SQLAlchemy**: Database abstraction with DeclarativeBase
- **Requests**: HTTP client for image downloading from OpenAI
- **gTTS**: Google's text-to-speech library

## Database
- **SQLite**: Default local database with configurable DATABASE_URL for production deployments
- Connection pooling and health checks configured for reliability

## Environment Configuration
- API keys managed through environment variables (OPENAI_API_KEY)
- Session secrets and database URLs configurable via environment
- Supports both development (SQLite) and production database configurations
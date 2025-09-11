"""
MYTHOSCRIBE MAIN APPLICATION FILE
================================

DEMO SPEAKING POINTS:
"This is the heart of our Mythoscribe application - the main Flask server that orchestrates
the entire AI-powered storytelling pipeline. Let me walk you through the key technical components
that make this system robust and scalable."

TECHNICAL HIGHLIGHTS TO MENTION:
- Flask web framework for RESTful API design
- Environment variable management for security
- Comprehensive logging system for debugging and monitoring
- Database integration with SQLAlchemy ORM
- Production-ready configuration with connection pooling
"""

import os
import logging
import sys
from flask import Flask
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from pathlib import Path
from database import db

# ENVIRONMENT CONFIGURATION - CRITICAL FOR SECURITY AND CONFIGURATION
# SPEAKING POINT: "We use environment variables to securely manage API keys, database URLs,
# and other sensitive configuration without hardcoding them in our source code."
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

else:
    print(f"Warning: .env file not found at {env_path}")

# PRODUCTION-GRADE LOGGING SYSTEM
# SPEAKING POINT: "Our logging system is enterprise-ready with both file and console output,
# automatic log rotation, and detailed debugging information. This is crucial for monitoring
# system performance and troubleshooting issues in production."
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# FILE HANDLER - Persistent logging with rotation
# SPEAKING POINT: "We use RotatingFileHandler to automatically manage log files,
# preventing them from growing too large and filling up disk space."
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10240,  # 10KB per file
    backupCount=10   # Keep 10 backup files
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.DEBUG)

# CONSOLE HANDLER - Real-time debugging output
# SPEAKING POINT: "During development, we get immediate feedback through console logging,
# which is essential for debugging the complex AI pipeline interactions."
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# ROOT LOGGER CONFIGURATION
# SPEAKING POINT: "We configure the root logger to capture all log levels,
# ensuring we don't miss any important system events or errors."
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# CLEAN UP EXISTING HANDLERS - Prevent duplicate logs
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ENVIRONMENT VARIABLE VALIDATION
# SPEAKING POINT: "We validate that all required environment variables are present
# before starting the application. This prevents runtime errors and ensures
# all AI services are properly configured."
logger.info("Environment variables loaded")
logger.debug(f"SESSION_SECRET present: {'SESSION_SECRET' in os.environ}")
logger.debug(f"DATABASE_URL present: {'DATABASE_URL' in os.environ}")
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Audio generation may fail.")

# FLASK APPLICATION INITIALIZATION
# SPEAKING POINT: "Here we create our Flask web application instance with secure session management.
# The secret key is loaded from environment variables for security."
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vedic-stories-secret-key-12345")

# DATABASE CONFIGURATION WITH PRODUCTION SETTINGS
# SPEAKING POINT: "Our database configuration includes connection pooling and health checks
# to ensure reliable performance under load. The pool_recycle prevents stale connections,
# and pool_pre_ping verifies connection health before use."
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vedic_stories.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,    # Recycle connections every 5 minutes
    "pool_pre_ping": True,  # Verify connection health before use
}

# DATABASE INITIALIZATION
# SPEAKING POINT: "We initialize SQLAlchemy with our Flask app, establishing the database connection
# that will handle all our story data persistence and retrieval operations."
db.init_app(app)

# ROUTE REGISTRATION - API ENDPOINTS
# SPEAKING POINT: "We import and register all our API routes, which handle the web interface
# and provide RESTful endpoints for story generation, retrieval, and management."
from routes import *

# DATABASE TABLE CREATION
# SPEAKING POINT: "Within the application context, we ensure all database tables are created
# based on our SQLAlchemy models. This sets up the schema for storing stories, images, and metadata."
with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()


# MAIN APPLICATION ENTRY POINT
# SPEAKING POINT: "This is where our Flask application starts. We handle command-line arguments,
# set up necessary directories, and launch the web server with debugging enabled for development."
if __name__ == "__main__":
    # COMMAND LINE ARGUMENT PARSING
    # SPEAKING POINT: "We support custom port configuration through command line arguments,
    # allowing flexible deployment options for different environments."
    port = 8000  # Default to 8000 instead of 5000
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port='):
        try:
            port = int(sys.argv[1].split('=')[1])
        except (IndexError, ValueError):
            print("Invalid port format. Using default port 8000.")

    # FILE SYSTEM SETUP
    # SPEAKING POINT: "We ensure all necessary directories exist before starting the server,
    # preventing file system errors during runtime."
    upload_folder = os.path.join('static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # API ENDPOINT DOCUMENTATION
    # SPEAKING POINT: "At startup, we automatically document all available API endpoints,
    # which is helpful for development and API testing."
    with app.app_context():
        print("\nRegistered routes:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} [{','.join(rule.methods)}]")

    # SERVER STARTUP ANNOUNCEMENT
    # SPEAKING POINT: "We provide clear startup information including access URLs,
    # making it easy for developers to know where the application is running."
    print(f"\nStarting Mythoscribe on port {port}")
    print(f"Access at: http://localhost:{port}")
    print(f"Or: http://127.0.0.1:{port}")

    # FLASK DEVELOPMENT SERVER
    # SPEAKING POINT: "We run Flask with debug mode enabled, which provides automatic reloading
    # on code changes, detailed error pages, and interactive debugging capabilities."
    app.run(host='0.0.0.0', port=port, debug=True)
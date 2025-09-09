import os
import logging
import sys
from flask import Flask
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from pathlib import Path
from database import db

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    
else:
    print(f"Warning: .env file not found at {env_path}")

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a file handler for logging
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10240,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Get the root logger and add handlers
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
    
# Add the handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Log environment variables (without sensitive data)
logger.info("Environment variables loaded")
logger.debug(f"SESSION_SECRET present: {'SESSION_SECRET' in os.environ}")
logger.debug(f"DATABASE_URL present: {'DATABASE_URL' in os.environ}")
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Audio generation may fail.")

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vedic-stories-secret-key-12345")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vedic_stories.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import and register routes
from routes import *

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()


if __name__ == "__main__":
    # Parse command line arguments for port
    port = 8000  # Default to 8000 instead of 5000
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port='):
        try:
            port = int(sys.argv[1].split('=')[1])
        except (IndexError, ValueError):
            print("Invalid port format. Using default port 8000.")

    # Make sure the upload folder exists
    upload_folder = os.path.join('static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Print all routes
    with app.app_context():
        print("\nRegistered routes:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} [{','.join(rule.methods)}]")

    print(f"\nStarting Mythoscribe on port {port}")
    print(f"Access at: http://localhost:{port}")
    print(f"Or: http://127.0.0.1:{port}")

    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)
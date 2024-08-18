from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Print the secret key to verify it's loaded
print("FLASK_SECRET_KEY:", os.getenv('FLASK_SECRET_KEY'))

import os
import json
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60 * 30  # 30 days

# Firebase credentials
CREDENTIALS = json.loads(os.getenv("CREDENTIALS"))
USER_DATABASE_NAME = os.getenv("USER_DATABASE_NAME")
TEACHER_DATABASE_NAME = os.getenv("TEACHER_DATABASE_NAME")

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
TEACHER_COLLECTION_NAME = "teachers"
USER_COLLECTION_NAME = "users"

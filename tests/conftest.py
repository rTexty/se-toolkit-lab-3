import os

# Set required environment variables before app imports
os.environ["API_TOKEN"] = "my-secret-api-key"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"

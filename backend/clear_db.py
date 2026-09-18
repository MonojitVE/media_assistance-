import os
import sys

# Add backend directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import Media

def clear_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database cleared successfully!")

if __name__ == "__main__":
    clear_db()

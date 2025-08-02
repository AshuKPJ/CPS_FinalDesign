# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# ⛓️ Get the DB connection URL from .env
DATABASE_URL = config("DATABASE_URL")

# ✅ Recommended for production: reconnect on idle disconnects
# Optionally add echo=True for SQL debug logging
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 🔄 automatically reconnects if idle connection is dead
    echo=False           # 🔧 set to True to log SQL queries
)

# 🎛️ Create a database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🏗️ Base class for your SQLAlchemy models
Base = declarative_base()

# 🔄 Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

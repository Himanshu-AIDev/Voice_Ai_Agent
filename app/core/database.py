# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv

# # 1. Load keys from .env.local
# load_dotenv(dotenv_path=".env.local")

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")

# # 2. Create the Connection String
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# # 3. Create the Engine
# # TiDB requires SSL; these arguments ensure it connects securely without needing a local certificate file
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"ssl": {"check_hostname": False, "verify_mode": "CERT_NONE"}}
# )

# # 4. Create the Session
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 5. Base for Models
# Base = declarative_base()

# # 6. Dependency for API
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import certifi  # <--- Fixes SSL for Mac/Windows
from dotenv import load_dotenv

# Load variables from .env.local
load_dotenv(".env.local")

# Construct URL from .env vars
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# --- SSL CONFIGURATION ---
# This automatically finds the correct SSL certificate path on your specific computer
ssl_args = {
    "ssl_ca": certifi.where()
}

# Construct the URL
# Note: We pass SSL config in connect_args below, not in the string itself
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- ENGINE CREATION ---
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"ssl": ssl_args},  # <--- Secure connection for TiDB
#     pool_pre_ping=True,              # <--- "Anti-Sleep": Checks if DB is alive before querying
#     pool_recycle=300,                # <--- Refreshes connection every 5 minutes
#     pool_size=10,
#     max_overflow=20
# )
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,

    connect_args={"ssl": ssl_args},

    pool_pre_ping=True,
    pool_recycle=180,      # 🔥 Lower → safer for cloud (3 min)
    
    pool_size=5,           # 🔥 Smaller = more stable in cloud
    max_overflow=10,

    pool_timeout=30,       # 🔥 Wait time before failing

    echo=False
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
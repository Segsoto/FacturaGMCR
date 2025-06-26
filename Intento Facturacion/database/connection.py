from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración para SQLite (más simple para desarrollo)
DATABASE_URL = "sqlite:///./granimar_facturacion.db"

# Para cambiar a SQL Server en el futuro, descomenta las siguientes líneas:
# DB_SERVER = os.getenv("DB_SERVER", "localhost")
# DB_DATABASE = os.getenv("DB_DATABASE", "granimar_facturacion")
# DB_USERNAME = os.getenv("DB_USERNAME", "sa")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "")
# DB_PORT = os.getenv("DB_PORT", "1433")
# DATABASE_URL = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependency para obtener la sesión de la base de datos
def get_db():
    """Obtener sesión de la base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

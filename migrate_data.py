import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

def migrate_database():
    load_dotenv()
    print("Starting database migration from SQLite to PostgreSQL...")
    
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    
    sqlite_url = f"sqlite:///{DATA_DIR / 'crime_news.db'}"
    postgres_url = os.environ.get("DATABASE_URL")
    
    if not postgres_url:
        print("Error: DATABASE_URL environment variable is not set.")
        return
        
    print(f"Connecting to source SQLite DB: {sqlite_url}")
    sqlite_engine = create_engine(sqlite_url)
    
    print(f"Connecting to target PostgreSQL DB...")
    postgres_engine = create_engine(postgres_url)
    
    # Create all tables in PostgreSQL
    print("Creating schema in PostgreSQL...")
    from app.database.database import initialize_database
    initialize_database()
    
    # We will use reflection to grab the tables
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    
    # Sort tables by dependencies (foreign keys)
    from sqlalchemy.schema import sort_tables
    sorted_tables = sort_tables(metadata.tables.values())
    
    with postgres_engine.connect() as pg_conn:
        with sqlite_engine.connect() as sq_conn:
            # Note: PostgreSQL might have foreign key constraints
            for table in sorted_tables:
                print(f"Migrating table: {table.name}...")
                
                # Fetch all data from SQLite
                rows = sq_conn.execute(table.select()).fetchall()
                if not rows:
                    print(f"  -> No data found in {table.name}, skipping.")
                    continue
                
                print(f"  -> Found {len(rows)} rows. Inserting into PostgreSQL...")
                
                # Convert rows to list of dicts
                dicts = [dict(row._mapping) for row in rows]
                
                # Insert into PostgreSQL
                pg_table = Table(table.name, MetaData(), autoload_with=postgres_engine)
                
                # Do it in chunks to avoid blowing up memory
                chunk_size = 500
                for i in range(0, len(dicts), chunk_size):
                    chunk = dicts[i:i + chunk_size]
                    pg_conn.execute(pg_table.insert(), chunk)
                    pg_conn.commit()
                
                print(f"  -> Successfully migrated {len(rows)} rows for {table.name}.")
                
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_database()

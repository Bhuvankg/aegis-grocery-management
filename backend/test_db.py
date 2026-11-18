
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 15}
)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        database, user = result.fetchone()

        print("AEGIS AI DATABASE CONNECTED!")
        print("Database:", database)
        print("User:", user)

except Exception as error:
    print("DATABASE CONNECTION FAILED:")
    print(type(error).__name__, error)

finally:
    engine.dispose()


from app.db.base import Base
from app.db.session import engine
from app import models


def initialize_database():
    print("Connecting to AEGIS AI database...")

    try:
        Base.metadata.create_all(bind=engine)

        print("SUCCESS: AEGIS AI tables created!")
        print("Database tables:")

        for table in Base.metadata.sorted_tables:
            print("-", table.name)

    except Exception as error:
        print("DATABASE INITIALIZATION FAILED")
        print(type(error).__name__, error)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    initialize_database()

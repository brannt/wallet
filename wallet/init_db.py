"""
DB initialization script. Waits for the DB to start up and creates the schema and prerequisite data.
"""
import sqlalchemy
from wallet.db import init_db
from wallet.settings import settings

if __name__ == "__main__":

    # Databases uses PyMySQL by default, while SQLAlchemy uses MySQLdb.
    # So we have to pass the driver explicitly.
    sqlalchemy_url = settings.DATABASE_URI.replace(
        "mysql://", "mysql+pymysql://"
    )
    engine = sqlalchemy.create_engine(sqlalchemy_url)
    for i in range(1000):
        print(f"Connecting, attempt {i}")
        try:
            engine.connect()
            break
        except:
            pass

    print("Creating tables")
    init_db(engine)

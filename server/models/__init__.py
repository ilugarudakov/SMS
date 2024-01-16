from .collector import CollectorModels, db
from .omnisell import MyEnums, OmnicellModel, db
# from .filler import StartData, db
from .users import Users
import sqlalchemy
from config import Config


class DbInit:
    collector = CollectorModels
    life = OmnicellModel

    @staticmethod
    def start() -> None:
        engine = sqlalchemy.create_engine(Config.DATABASE.DB_URL)
        conn = engine.connect()
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DATABASE.DB_NAME}")
        conn.close()
        db.create_all()
        # StartData.fill()

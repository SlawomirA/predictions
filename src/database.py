from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Konfiguracja dla mojej bazy danych
MY_DATABASE_URL = "mysql+pymysql://avnadmin:AVNS_eLz9N377f8FIlFPl3Db@thesis-thesis.l.aivencloud.com:10454/defaultdb"

engine_1 = create_engine(
    MY_DATABASE_URL,
    pool_size=5,
    max_overflow=10
)

SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine_1)

# Konfiguracja dla bazy rekrutacyjnej sid
SQLALCHEMY_DATABASE_URL_2 = "oracle+cx_oracle://j_sid_rek_ws:R0cK7#aTB0dY8l4ck3YEdpeA$@sid.p.lodz.pl:1522/dbsid"

engine_2 = create_engine(
    SQLALCHEMY_DATABASE_URL_2,
    pool_size=5,
    max_overflow=10
)

try:
    # Utworzenie silnika połączenia
    engine = create_engine(SQLALCHEMY_DATABASE_URL_2)

    # Testowe połączenie
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 FROM DUAL"))
        for row in result:
            print("Test połączenia sid udany:", row)
except Exception as e:
    print("Błąd podczas testu sid połączenia:", e)


SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine_2)

Base = declarative_base()

def get_my_db():
    db = SessionLocal1()
    try:
        yield db
    finally:
        db.close()

def get_sid_db():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()



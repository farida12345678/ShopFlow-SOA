from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://shopflow:shopflow123@localhost:5432/shopflow"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connexion réussie !")
        print(result.scalar())
except Exception as e:
    print("Erreur de connexion :")
    print(e)
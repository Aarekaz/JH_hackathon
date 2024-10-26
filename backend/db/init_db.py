from db.database import Base, engine

def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()


from shared.dao.session import engine
from shared.domains.domains import Base


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine) 
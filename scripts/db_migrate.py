#!/usr/bin/env python3
"""Database migration script - creates all tables."""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.models import Base, engine
except ImportError as e:
    logger.error(f"Failed to import models: {e}")
    sys.exit(1)


def main():
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to create tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Automated unit tests for Lab 6: SQLite Database Schema & URL Table.
Tests ORM model URLItem, session lifecycle, constraints, and persistence.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import URLItem


@pytest.fixture(scope="function")
def test_db_session():
    """Provides a fresh, isolated in-memory SQLite database session for each test."""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_and_retrieve_url_item(test_db_session):
    """Verify storing a long URL with short code and retrieving it."""
    item = URLItem(
        short_code="test01",
        original_url="https://aws.amazon.com/well-architected/",
        click_count=0,
    )
    test_db_session.add(item)
    test_db_session.commit()

    retrieved = test_db_session.query(URLItem).filter(URLItem.short_code == "test01").first()
    assert retrieved is not None
    assert retrieved.id is not None
    assert retrieved.short_code == "test01"
    assert retrieved.original_url == "https://aws.amazon.com/well-architected/"
    assert retrieved.click_count == 0
    assert retrieved.is_active is True
    assert retrieved.created_at is not None


def test_unique_short_code_constraint(test_db_session):
    """Verify SQLite enforces unique constraint on the short_code column."""
    item1 = URLItem(
        short_code="duplicate-code",
        original_url="https://aws.amazon.com/s3/",
    )
    test_db_session.add(item1)
    test_db_session.commit()

    # Attempt inserting a second record with identical short_code
    item2 = URLItem(
        short_code="duplicate-code",
        original_url="https://aws.amazon.com/ec2/",
    )
    test_db_session.add(item2)
    with pytest.raises(IntegrityError):
        test_db_session.commit()
    test_db_session.rollback()


def test_update_click_count(test_db_session):
    """Verify click counter can be incremented and persisted."""
    item = URLItem(
        short_code="click-test",
        original_url="https://aws.amazon.com/cloudwatch/",
        click_count=0,
    )
    test_db_session.add(item)
    test_db_session.commit()

    # Increment
    item.click_count += 1
    test_db_session.commit()

    updated = test_db_session.query(URLItem).filter(URLItem.short_code == "click-test").first()
    assert updated.click_count == 1

"""
Database Seeding & Verification Script for Lab 6.
Demonstrates direct SQLite database connection, table creation, and storing records.
"""
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, SessionLocal, engine, init_db
from app.models import URLItem
from app.utils import generate_short_code


def main():
    print("=" * 60)
    print("Lab 6: SQLite Database Initialization & Seeding")
    print("=" * 60)

    # 1. Initialize Database Tables
    print("1. Creating SQLite database & 'urls' table...")
    init_db()
    print("   -> Success: Database schema verified.")

    # 2. Open DB Session
    db = SessionLocal()

    try:
        # Sample long URLs to store
        seed_data = [
            ("aws-ec2", "https://aws.amazon.com/ec2/"),
            ("aws-s3", "https://aws.amazon.com/s3/"),
            ("aws-rds", "https://aws.amazon.com/rds/"),
            (generate_short_code(6), "https://aws.amazon.com/dynamodb/"),
            (generate_short_code(6), "https://aws.amazon.com/lambda/"),
        ]

        print("\n2. Storing long URLs and short codes into SQLite database...")
        for code, url in seed_data:
            # Check if record already exists
            existing = db.query(URLItem).filter(URLItem.short_code == code).first()
            if not existing:
                item = URLItem(
                    short_code=code,
                    original_url=url,
                    click_count=0,
                )
                db.add(item)
                print(f"   [INSERTED] Short Code: '{code}' -> Target: '{url}'")
            else:
                print(f"   [EXISTS]   Short Code: '{code}' -> Target: '{url}'")

        db.commit()
        print("   -> Transaction successfully committed to SQLite disk!")

        # 3. Query & Verify Stored Records
        print("\n3. Querying stored records from 'urls' table:")
        all_records = db.query(URLItem).all()
        print(f"   Total records in SQLite: {len(all_records)}")
        print("-" * 60)
        print(f"{'ID':<4} | {'Short Code':<12} | {'Clicks':<6} | {'Target URL'}")
        print("-" * 60)
        for r in all_records:
            print(f"{r.id:<4} | {r.short_code:<12} | {r.click_count:<6} | {r.original_url}")
        print("-" * 60)

    finally:
        db.close()
        print("\nDatabase session closed cleanly.")


if __name__ == "__main__":
    main()

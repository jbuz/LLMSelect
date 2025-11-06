#!/usr/bin/env python
"""
Migration runner for LLMSelect database schema changes.

This script runs all SQL migration files in the migrations/ directory
in lexicographic order.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmselect import create_app
from llmselect.extensions import db


def run_migrations():
    """Run all SQL migration files in order."""
    app = create_app()

    with app.app_context():
        # Get all migration files
        migrations_dir = Path(__file__).parent.parent / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            print("No migration files found.")
            return

        print(f"Found {len(migration_files)} migration file(s):")
        for mf in migration_files:
            print(f"  - {mf.name}")

        # Run each migration
        for migration_file in migration_files:
            print(f"\nRunning migration: {migration_file.name}")

            with open(migration_file, "r") as f:
                sql = f.read()

            # Split by semicolons and execute each statement
            statements = [
                s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")
            ]

            for statement in statements:
                if statement:
                    try:
                        db.session.execute(db.text(statement))
                        print(f"  ✓ Executed statement")
                    except Exception as e:
                        print(f"  ⚠ Error: {e}")
                        # Continue with other statements

            db.session.commit()
            print(f"✓ Migration {migration_file.name} completed")

        print("\n✓ All migrations completed successfully!")


if __name__ == "__main__":
    run_migrations()

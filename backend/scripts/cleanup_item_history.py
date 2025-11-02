"""
Cleanup script for item_history table.

This script removes old item_history records older than the specified retention period.
By default, it keeps 30 days of history. This helps prevent the audit trail table
from growing indefinitely.

Usage:
    python -m scripts.cleanup_item_history [--days 30] [--dry-run]

Future enhancement:
    This script can be scheduled as a Celery periodic task once Celery is set up in Phase 3.
    Future work may also aggregate old data into compressed statistics/trends before deletion.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.config import settings


def cleanup_old_item_history(
    retention_days: int = 30,
    dry_run: bool = False,
    db: Session | None = None,
) -> int:
    """
    Clean up old item_history records.

    Args:
        retention_days: Number of days of history to keep (default: 30)
        dry_run: If True, only count records that would be deleted without deleting them
        db: Optional database session (creates new one if not provided)

    Returns:
        Number of records deleted (or would be deleted in dry-run mode)
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        if dry_run:
            # Count records that would be deleted
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            result = db.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM item_history 
                    WHERE timestamp < :cutoff_date
                """),
                {"cutoff_date": cutoff_date},
            )
            count = result.scalar() or 0
            print(f"[DRY RUN] Would delete {count} records older than {retention_days} days")
            return count
        else:
            # Use the database function for efficient deletion
            result = db.execute(
                text("SELECT cleanup_old_item_history(:retention_days)"),
                {"retention_days": retention_days},
            )
            deleted_count = result.scalar() or 0
            db.commit()
            print(f"Deleted {deleted_count} records older than {retention_days} days")
            return deleted_count
    except Exception as e:
        if not dry_run:
            db.rollback()
        print(f"Error during cleanup: {e}", file=sys.stderr)
        raise
    finally:
        if should_close:
            db.close()


def main():
    """CLI entry point for the cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up old item_history records",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run: see how many records would be deleted
  python -m scripts.cleanup_item_history --dry-run

  # Delete records older than 30 days (default)
  python -m scripts.cleanup_item_history

  # Delete records older than 60 days
  python -m scripts.cleanup_item_history --days 60
        """,
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of history to keep (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    args = parser.parse_args()

    if args.days < 1:
        print("Error: retention_days must be at least 1", file=sys.stderr)
        sys.exit(1)

    try:
        deleted_count = cleanup_old_item_history(
            retention_days=args.days,
            dry_run=args.dry_run,
        )
        sys.exit(0)
    except Exception as e:
        print(f"Cleanup failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


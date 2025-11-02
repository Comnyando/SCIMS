"""
Create a developer user with admin permissions for local development.

This script creates a developer user that:
- Has full admin access (owner role in all organizations)
- Only runs in development environment
- Is marked as active and verified

WARNING: This script is for LOCAL DEVELOPMENT ONLY and should NEVER run in production.

Usage:
    python -m scripts.create_dev_user
    
Or from the backend directory:
    python scripts/create_dev_user.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Organization, OrganizationMember
from app.core.security import hash_password
from app.config import settings

# Developer user credentials (LOCAL DEVELOPMENT ONLY)
DEV_EMAIL = "dev@scims.local"
DEV_USERNAME = "dev"
DEV_PASSWORD = "dev123"  # Change this if needed, but keep it simple for local dev
DEV_ORG_NAME = "Developer Organization"
DEV_ORG_SLUG = "dev-org"


def create_dev_user(db: Session) -> User:
    """Create or update the developer user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == DEV_EMAIL).first()
    
    if existing_user:
        # Update existing user to ensure it's active and verified
        existing_user.username = DEV_USERNAME
        existing_user.hashed_password = hash_password(DEV_PASSWORD)
        existing_user.is_active = True
        existing_user.is_verified = True
        print(f"Updated existing developer user: {DEV_EMAIL}")
        db.flush()
        return existing_user
    
    # Create new developer user
    dev_user = User(
        email=DEV_EMAIL,
        username=DEV_USERNAME,
        hashed_password=hash_password(DEV_PASSWORD),
        is_active=True,
        is_verified=True,
    )
    db.add(dev_user)
    db.flush()
    print(f"Created developer user: {DEV_EMAIL}")
    return dev_user


def ensure_dev_organization(db: Session, dev_user: User) -> Organization:
    """Create or get the developer organization and ensure dev_user is owner."""
    # Check if organization already exists
    existing_org = db.query(Organization).filter(Organization.slug == DEV_ORG_SLUG).first()
    
    if existing_org:
        org = existing_org
        print(f"Using existing developer organization: {DEV_ORG_NAME}")
    else:
        org = Organization(
            name=DEV_ORG_NAME,
            slug=DEV_ORG_SLUG,
            description="Developer organization for local development and testing",
        )
        db.add(org)
        db.flush()
        print(f"Created developer organization: {DEV_ORG_NAME}")
    
    # Ensure dev_user is owner of the organization
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == dev_user.id,
            OrganizationMember.organization_id == org.id,
        )
        .first()
    )
    
    if membership:
        # Update to ensure owner role
        if membership.role != "owner":
            membership.role = "owner"
            print(f"Updated membership role to owner for {DEV_EMAIL} in {DEV_ORG_NAME}")
    else:
        membership = OrganizationMember(
            organization_id=org.id,
            user_id=dev_user.id,
            role="owner",
        )
        db.add(membership)
        print(f"Added {DEV_EMAIL} as owner of {DEV_ORG_NAME}")
    
    db.flush()
    return org


def add_dev_user_to_all_orgs(db: Session, dev_user: User) -> None:
    """Add developer user as owner to all existing organizations."""
    all_orgs = db.query(Organization).all()
    
    for org in all_orgs:
        # Skip the dev organization (already handled)
        if org.slug == DEV_ORG_SLUG:
            continue
        
        # Check if already a member
        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == dev_user.id,
                OrganizationMember.organization_id == org.id,
            )
            .first()
        )
        
        if membership:
            # Update to owner role
            if membership.role != "owner":
                membership.role = "owner"
                print(f"Updated {DEV_EMAIL} to owner of {org.name}")
        else:
            # Add as owner
            membership = OrganizationMember(
                organization_id=org.id,
                user_id=dev_user.id,
                role="owner",
            )
            db.add(membership)
            print(f"Added {DEV_EMAIL} as owner of {org.name}")


def main():
    """Main function to create developer user."""
    # Safety check: Only run in development
    if settings.environment != "development":
        print("=" * 60)
        print("ERROR: This script can only run in development environment!")
        print(f"Current environment: {settings.environment}")
        print("=" * 60)
        sys.exit(1)
    
    print("=" * 60)
    print("Creating Developer User (LOCAL DEVELOPMENT ONLY)")
    print("=" * 60)
    print()
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created.")
    print()
    
    db: Session = SessionLocal()
    try:
        # Create developer user
        dev_user = create_dev_user(db)
        print()
        
        # Ensure developer organization exists and dev_user is owner
        dev_org = ensure_dev_organization(db, dev_user)
        print()
        
        # Add dev_user as owner to all existing organizations
        print("Adding developer user to all existing organizations...")
        add_dev_user_to_all_orgs(db, dev_user)
        print()
        
        # Commit all changes
        db.commit()
        print("=" * 60)
        print("Developer user created successfully!")
        print()
        print("Developer Account:")
        print(f"  Email: {DEV_EMAIL}")
        print(f"  Username: {DEV_USERNAME}")
        print(f"  Password: {DEV_PASSWORD}")
        print(f"  Status: Active & Verified")
        print(f"  Role: Owner of all organizations")
        print()
        print("You can now log in using these credentials in your local development environment.")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating developer user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


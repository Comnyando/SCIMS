"""
Seed data script for development and testing.

This script creates sample users, organizations, and memberships
for local development and testing purposes.

Usage:
    python -m scripts.seed_data
    
Or from the backend directory:
    python scripts/seed_data.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Organization, OrganizationMember
from passlib.context import CryptContext

# Password hashing context
# Note: You'll need to install passlib and argon2: pip install passlib[argon2]
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def create_test_users(db: Session) -> dict[str, User]:
    """Create test users and return a dictionary mapping email to User."""
    users_data = [
        {
            "email": "admin@scims.test",
            "username": "admin",
            "hashed_password": hash_password("admin123"),
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "owner@scims.test",
            "username": "owner",
            "hashed_password": hash_password("owner123"),
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "member@scims.test",
            "username": "member",
            "hashed_password": hash_password("member123"),
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "viewer@scims.test",
            "username": "viewer",
            "hashed_password": hash_password("viewer123"),
            "is_active": True,
            "is_verified": True,
        },
    ]
    
    users = {}
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            users[user_data["email"]] = existing_user
        else:
            user = User(**user_data)
            db.add(user)
            db.flush()
            users[user_data["email"]] = user
            print(f"Created user: {user_data['email']}")
    
    return users


def create_test_organizations(db: Session) -> dict[str, Organization]:
    """Create test organizations and return a dictionary mapping name to Organization."""
    orgs_data = [
        {
            "name": "Test Organization",
            "slug": "test-org",
            "description": "A test organization for development",
        },
        {
            "name": "Another Organization",
            "slug": "another-org",
            "description": "Another test organization",
        },
    ]
    
    organizations = {}
    for org_data in orgs_data:
        # Check if organization already exists
        existing_org = db.query(Organization).filter(Organization.slug == org_data["slug"]).first()
        if existing_org:
            print(f"Organization {org_data['name']} already exists, skipping...")
            organizations[org_data["name"]] = existing_org
        else:
            org = Organization(**org_data)
            db.add(org)
            db.flush()
            organizations[org_data["name"]] = org
            print(f"Created organization: {org_data['name']}")
    
    return organizations


def create_memberships(
    db: Session,
    users: dict[str, User],
    organizations: dict[str, Organization],
) -> None:
    """Create organization memberships."""
    memberships = [
        {
            "organization": organizations["Test Organization"],
            "user": users["admin@scims.test"],
            "role": "admin",
        },
        {
            "organization": organizations["Test Organization"],
            "user": users["owner@scims.test"],
            "role": "owner",
        },
        {
            "organization": organizations["Test Organization"],
            "user": users["member@scims.test"],
            "role": "member",
        },
        {
            "organization": organizations["Test Organization"],
            "user": users["viewer@scims.test"],
            "role": "viewer",
        },
        {
            "organization": organizations["Another Organization"],
            "user": users["admin@scims.test"],
            "role": "owner",
        },
    ]
    
    for membership_data in memberships:
        # Check if membership already exists
        existing = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == membership_data["organization"].id,
                OrganizationMember.user_id == membership_data["user"].id,
            )
            .first()
        )
        
        if existing:
            print(
                f"Membership {membership_data['user'].email} -> "
                f"{membership_data['organization'].name} already exists, skipping..."
            )
        else:
            member = OrganizationMember(
                organization_id=membership_data["organization"].id,
                user_id=membership_data["user"].id,
                role=membership_data["role"],
            )
            db.add(member)
            print(
                f"Created membership: {membership_data['user'].email} ({membership_data['role']}) -> "
                f"{membership_data['organization'].name}"
            )


def main():
    """Main seed function."""
    print("Starting seed data script...")
    print("=" * 50)
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created.")
    print()
    
    db: Session = SessionLocal()
    try:
        # Create test data
        users = create_test_users(db)
        print()
        
        organizations = create_test_organizations(db)
        print()
        
        create_memberships(db, users, organizations)
        print()
        
        # Commit all changes
        db.commit()
        print("=" * 50)
        print("Seed data created successfully!")
        print()
        print("Test users created:")
        for email, user in users.items():
            print(f"  - {email} (username: {user.username})")
        print()
        print("Test organizations created:")
        for name, org in organizations.items():
            print(f"  - {name} (slug: {org.slug})")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating seed data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


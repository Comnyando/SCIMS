"""Initial schema: users, organizations, organization_members

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='User email address (unique, used for login)'),
        sa.Column('username', sa.String(length=100), nullable=True, comment='Optional username for display'),
        sa.Column('hashed_password', sa.String(length=255), nullable=True, comment='Argon2 hashed password (nullable for OAuth users)'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether the user account is active'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false', comment='Whether the user email has been verified'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
        comment='User accounts and authentication data'
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Organization name'),
        sa.Column('slug', sa.String(length=100), nullable=True, comment='URL-friendly identifier (optional, for future public pages)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Organization description'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        comment='Organizations (teams/groups) for collaborative inventory management'
    )
    op.create_index('ix_organizations_name', 'organizations', ['name'])
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    
    # Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the organization'),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the user'),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member', comment='User role in the organization (owner, admin, member, viewer)'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the user joined the organization'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_member_user_org'),
        comment='Many-to-many relationship between users and organizations'
    )
    op.create_index('ix_organization_members_org_id', 'organization_members', ['organization_id'])
    op.create_index('ix_organization_members_user_id', 'organization_members', ['user_id'])
    op.create_index('ix_organization_members_role', 'organization_members', ['role'])
    
    # Create function and trigger to automatically update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create triggers for users and organizations tables
    op.execute("""
        CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_organizations_updated_at 
        BEFORE UPDATE ON organizations 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers first
    op.execute('DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;')
    op.execute('DROP TRIGGER IF EXISTS update_users_updated_at ON users;')
    
    # Drop function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column();')
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_index('ix_organization_members_role', table_name='organization_members')
    op.drop_index('ix_organization_members_user_id', table_name='organization_members')
    op.drop_index('ix_organization_members_org_id', table_name='organization_members')
    op.drop_table('organization_members')
    
    op.drop_index('ix_organizations_slug', table_name='organizations')
    op.drop_index('ix_organizations_name', table_name='organizations')
    op.drop_table('organizations')
    
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')


"""add_canonical_locations_support

Revision ID: 4fe1b28b8fa5
Revises: d717c1642e4d
Create Date: 2025-11-01 13:48:21.135470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4fe1b28b8fa5'
down_revision: Union[str, None] = 'd717c1642e4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add canonical location support fields to locations table
    op.add_column('locations', sa.Column('is_canonical', sa.Boolean(), nullable=False, server_default='false', comment='Whether this is a canonical/public location that many players reference'))
    op.add_column('locations', sa.Column('canonical_location_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Reference to canonical location (for player locations that are at a canonical location)'))
    op.add_column('locations', sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=True, comment='User who created this canonical location (nullable for user-owned locations)'))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_locations_canonical_location',
        'locations', 'locations',
        ['canonical_location_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_locations_created_by',
        'locations', 'users',
        ['created_by'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes for performance
    op.create_index('ix_locations_is_canonical', 'locations', ['is_canonical'])
    op.create_index('ix_locations_canonical_location_id', 'locations', ['canonical_location_id'])
    op.create_index('ix_locations_created_by', 'locations', ['created_by'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_locations_created_by', table_name='locations')
    op.drop_index('ix_locations_canonical_location_id', table_name='locations')
    op.drop_index('ix_locations_is_canonical', table_name='locations')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_locations_created_by', 'locations', type_='foreignkey')
    op.drop_constraint('fk_locations_canonical_location', 'locations', type_='foreignkey')
    
    # Drop columns
    op.drop_column('locations', 'created_by')
    op.drop_column('locations', 'canonical_location_id')
    op.drop_column('locations', 'is_canonical')


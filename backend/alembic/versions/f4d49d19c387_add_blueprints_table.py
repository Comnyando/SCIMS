"""add_blueprints_table

Revision ID: f4d49d19c387
Revises: 4fe1b28b8fa5
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f4d49d19c387'
down_revision: Union[str, None] = '4fe1b28b8fa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create blueprints table
    op.create_table(
        'blueprints',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Blueprint name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Blueprint description'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='Blueprint category (e.g., Weapons, Components, Food)'),
        sa.Column('crafting_time_minutes', sa.Integer(), nullable=False, server_default='0', comment='Crafting time in minutes (0 = instant)'),
        sa.Column('output_item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Item produced by this blueprint'),
        sa.Column('output_quantity', sa.Numeric(precision=15, scale=3), nullable=False, comment='Quantity of output item produced'),
        sa.Column('blueprint_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Blueprint ingredients and metadata (JSON)'),
        sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False, comment='User who created this blueprint'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false', comment='Whether blueprint is publicly visible'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0', comment='Number of times this blueprint has been used (for popularity tracking)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['output_item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        comment='Crafting blueprints defining item production'
    )
    
    # Create indexes
    op.create_index('ix_blueprints_name', 'blueprints', ['name'])
    op.create_index('ix_blueprints_category', 'blueprints', ['category'])
    op.create_index('ix_blueprints_output_item_id', 'blueprints', ['output_item_id'])
    op.create_index('ix_blueprints_created_by', 'blueprints', ['created_by'])
    op.create_index('ix_blueprints_is_public', 'blueprints', ['is_public'])
    op.create_index('ix_blueprints_usage_count', 'blueprints', ['usage_count'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_blueprints_usage_count', table_name='blueprints')
    op.drop_index('ix_blueprints_is_public', table_name='blueprints')
    op.drop_index('ix_blueprints_created_by', table_name='blueprints')
    op.drop_index('ix_blueprints_output_item_id', table_name='blueprints')
    op.drop_index('ix_blueprints_category', table_name='blueprints')
    op.drop_index('ix_blueprints_name', table_name='blueprints')
    
    # Drop table
    op.drop_table('blueprints')


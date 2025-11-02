"""add_resource_sources_tables

Revision ID: c8d7e9f0a1b2
Revises: b2a696029f90
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c8d7e9f0a1b2'
down_revision: Union[str, None] = 'b2a696029f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create resource_sources table
    op.create_table(
        'resource_sources',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the item this source provides'),
        sa.Column('source_type', sa.String(length=50), nullable=False, comment='Source type: player_stock, universe_location, trading_post'),
        sa.Column('source_identifier', sa.String(length=255), nullable=False, comment='Identifier for the source (player_id, location_name, etc.)'),
        sa.Column('available_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0', comment='Available quantity at this source'),
        sa.Column('cost_per_unit', sa.Numeric(precision=15, scale=3), nullable=True, comment='Cost per unit (nullable, for trading posts or player trades)'),
        sa.Column('last_verified', sa.DateTime(timezone=True), nullable=True, comment='Last time this source was verified'),
        sa.Column('reliability_score', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.5', comment='Reliability score (0-1) based on verification history'),
        sa.Column('source_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional source metadata (JSON)'),
        sa.Column('location_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Optional location where this source can be found (for universe locations, trading posts, etc.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='SET NULL'),
        comment='Resource sources tracking where items can be obtained'
    )

    # Create indexes for resource_sources
    op.create_index('ix_resource_sources_item_id', 'resource_sources', ['item_id'])
    op.create_index('ix_resource_sources_source_type', 'resource_sources', ['source_type'])
    op.create_index('ix_resource_sources_source_identifier', 'resource_sources', ['source_identifier'])
    op.create_index('ix_resource_sources_item_type', 'resource_sources', ['item_id', 'source_type'])
    op.create_index('ix_resource_sources_reliability', 'resource_sources', ['reliability_score'])
    op.create_index('ix_resource_sources_last_verified', 'resource_sources', ['last_verified'])
    op.create_index('ix_resource_sources_location_id', 'resource_sources', ['location_id'])

    # Create source_verification_log table
    op.create_table(
        'source_verification_log',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('source_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the resource source'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=False), nullable=False, comment='User who performed the verification'),
        sa.Column('verified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when verification was performed'),
        sa.Column('was_accurate', sa.Boolean(), nullable=False, comment='Whether the source information was accurate'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Optional notes about the verification'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['resource_sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='CASCADE'),
        comment='Log of source verifications for reliability scoring'
    )

    # Create indexes for source_verification_log
    op.create_index('ix_source_verification_log_source_id', 'source_verification_log', ['source_id'])
    op.create_index('ix_source_verification_log_verified_by', 'source_verification_log', ['verified_by'])
    op.create_index('ix_source_verification_log_verified_at', 'source_verification_log', ['verified_at'])
    op.create_index('ix_source_verification_log_was_accurate', 'source_verification_log', ['was_accurate'])


def downgrade() -> None:
    # Drop indexes for source_verification_log
    op.drop_index('ix_source_verification_log_was_accurate', table_name='source_verification_log')
    op.drop_index('ix_source_verification_log_verified_at', table_name='source_verification_log')
    op.drop_index('ix_source_verification_log_verified_by', table_name='source_verification_log')
    op.drop_index('ix_source_verification_log_source_id', table_name='source_verification_log')

    # Drop source_verification_log table
    op.drop_table('source_verification_log')

    # Drop indexes for resource_sources
    op.drop_index('ix_resource_sources_location_id', table_name='resource_sources')
    op.drop_index('ix_resource_sources_last_verified', table_name='resource_sources')
    op.drop_index('ix_resource_sources_reliability', table_name='resource_sources')
    op.drop_index('ix_resource_sources_item_type', table_name='resource_sources')
    op.drop_index('ix_resource_sources_source_identifier', table_name='resource_sources')
    op.drop_index('ix_resource_sources_source_type', table_name='resource_sources')
    op.drop_index('ix_resource_sources_item_id', table_name='resource_sources')

    # Drop resource_sources table
    op.drop_table('resource_sources')


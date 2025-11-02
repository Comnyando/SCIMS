"""add_analytics_tables

Revision ID: 8c94020b6137
Revises: b65cb0724599
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8c94020b6137'
down_revision: Union[str, None] = 'b65cb0724599'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add analytics_consent field to users table
    op.add_column(
        'users',
        sa.Column(
            'analytics_consent',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Whether user has consented to analytics data collection'
        )
    )
    
    # Create usage_events table
    op.create_table(
        'usage_events',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True, comment='User who triggered the event (nullable for anonymous events)'),
        sa.Column('event_type', sa.String(length=100), nullable=False, comment='Type of event (e.g., blueprint_used, goal_created, item_stock_updated)'),
        sa.Column('entity_type', sa.String(length=50), nullable=True, comment='Type of entity involved (e.g., blueprint, goal, item)'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=False), nullable=True, comment='ID of the entity involved'),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional event-specific data (JSON)'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address (anonymized if required)'),
        sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User agent string (truncated)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the event occurred'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        comment='Usage events for analytics (requires user consent)'
    )
    
    # Create indexes for usage_events
    op.create_index('ix_usage_events_user_id', 'usage_events', ['user_id'])
    op.create_index('ix_usage_events_event_type', 'usage_events', ['event_type'])
    op.create_index('ix_usage_events_entity_type', 'usage_events', ['entity_type'])
    op.create_index('ix_usage_events_entity_id', 'usage_events', ['entity_id'])
    op.create_index('ix_usage_events_created_at', 'usage_events', ['created_at'])
    op.create_index('ix_usage_events_user_event', 'usage_events', ['user_id', 'event_type'])
    
    # Create recipe_usage_stats table (aggregated statistics)
    op.create_table(
        'recipe_usage_stats',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('blueprint_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Blueprint this stat is for'),
        sa.Column('period_start', sa.Date(), nullable=False, comment='Start of the aggregation period'),
        sa.Column('period_end', sa.Date(), nullable=False, comment='End of the aggregation period'),
        sa.Column('period_type', sa.String(length=20), nullable=False, comment='Type of period: daily, weekly, monthly'),
        sa.Column('total_uses', sa.Integer(), nullable=False, server_default='0', comment='Total number of times blueprint was used'),
        sa.Column('unique_users', sa.Integer(), nullable=False, server_default='0', comment='Number of unique users who used this blueprint'),
        sa.Column('completed_count', sa.Integer(), nullable=False, server_default='0', comment='Number of completed crafts'),
        sa.Column('cancelled_count', sa.Integer(), nullable=False, server_default='0', comment='Number of cancelled crafts'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the stat was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the stat was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['blueprint_id'], ['blueprints.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('blueprint_id', 'period_start', 'period_end', 'period_type', name='uq_recipe_stats_period'),
        comment='Aggregated usage statistics for blueprints'
    )
    
    # Create indexes for recipe_usage_stats
    op.create_index('ix_recipe_usage_stats_blueprint_id', 'recipe_usage_stats', ['blueprint_id'])
    op.create_index('ix_recipe_usage_stats_period', 'recipe_usage_stats', ['period_start', 'period_end'])
    op.create_index('ix_recipe_usage_stats_period_type', 'recipe_usage_stats', ['period_type'])
    
    # Create trigger for recipe_usage_stats updated_at
    op.execute("""
        CREATE TRIGGER update_recipe_usage_stats_updated_at 
        BEFORE UPDATE ON recipe_usage_stats 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_recipe_usage_stats_updated_at ON recipe_usage_stats;")
    
    # Drop indexes
    op.drop_index('ix_recipe_usage_stats_period_type', table_name='recipe_usage_stats')
    op.drop_index('ix_recipe_usage_stats_period', table_name='recipe_usage_stats')
    op.drop_index('ix_recipe_usage_stats_blueprint_id', table_name='recipe_usage_stats')
    op.drop_index('ix_usage_events_user_event', table_name='usage_events')
    op.drop_index('ix_usage_events_created_at', table_name='usage_events')
    op.drop_index('ix_usage_events_entity_id', table_name='usage_events')
    op.drop_index('ix_usage_events_entity_type', table_name='usage_events')
    op.drop_index('ix_usage_events_event_type', table_name='usage_events')
    op.drop_index('ix_usage_events_user_id', table_name='usage_events')
    
    # Drop tables
    op.drop_table('recipe_usage_stats')
    op.drop_table('usage_events')
    
    # Remove analytics_consent column
    op.drop_column('users', 'analytics_consent')


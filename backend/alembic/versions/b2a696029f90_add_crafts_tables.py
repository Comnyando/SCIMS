"""add_crafts_tables

Revision ID: b2a696029f90
Revises: f4d49d19c387
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b2a696029f90'
down_revision: Union[str, None] = 'f4d49d19c387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create crafts table
    op.create_table(
        'crafts',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('blueprint_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the blueprint'),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Organization this craft belongs to (nullable)'),
        sa.Column('requested_by', postgresql.UUID(as_uuid=False), nullable=False, comment='User who requested this craft'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='planned', comment='Craft status: planned, in_progress, completed, cancelled'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0', comment='Craft priority (higher = more important)'),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True, comment='Scheduled start time (nullable)'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='Actual start time (nullable)'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion time (nullable)'),
        sa.Column('output_location_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Location where output items will be placed'),
        sa.Column('craft_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional craft metadata (JSON)'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['blueprint_id'], ['blueprints.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['output_location_id'], ['locations.id'], ondelete='RESTRICT'),
        comment='Crafting operations tracking'
    )

    # Create indexes for crafts
    op.create_index('ix_crafts_blueprint_id', 'crafts', ['blueprint_id'])
    op.create_index('ix_crafts_organization_id', 'crafts', ['organization_id'])
    op.create_index('ix_crafts_requested_by', 'crafts', ['requested_by'])
    op.create_index('ix_crafts_status', 'crafts', ['status'])
    op.create_index('ix_crafts_status_organization', 'crafts', ['status', 'organization_id'])

    # Create craft_ingredients table
    op.create_table(
        'craft_ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('craft_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the craft'),
        sa.Column('item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the ingredient item'),
        sa.Column('required_quantity', sa.Numeric(precision=15, scale=3), nullable=False, comment='Required quantity of this ingredient'),
        sa.Column('source_location_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Location where ingredient will be sourced from (nullable)'),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='stock', comment='Source type: stock, player, universe'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='Ingredient status: pending, reserved, fulfilled'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('craft_id', 'item_id', name='uq_craft_ingredient_craft_item'),
        sa.ForeignKeyConstraint(['craft_id'], ['crafts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['source_location_id'], ['locations.id'], ondelete='SET NULL'),
        comment='Individual ingredients for each craft operation'
    )

    # Create indexes for craft_ingredients
    op.create_index('ix_craft_ingredients_craft_id', 'craft_ingredients', ['craft_id'])
    op.create_index('ix_craft_ingredients_item_id', 'craft_ingredients', ['item_id'])
    op.create_index('ix_craft_ingredients_status', 'craft_ingredients', ['status'])

    # Add foreign key constraint for item_history.related_craft_id (was added earlier but FK deferred)
    op.create_foreign_key(
        'fk_item_history_related_craft',
        'item_history',
        'crafts',
        ['related_craft_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key for item_history.related_craft_id first
    op.drop_constraint('fk_item_history_related_craft', 'item_history', type_='foreignkey')

    # Drop indexes for craft_ingredients
    op.drop_index('ix_craft_ingredients_status', table_name='craft_ingredients')
    op.drop_index('ix_craft_ingredients_item_id', table_name='craft_ingredients')
    op.drop_index('ix_craft_ingredients_craft_id', table_name='craft_ingredients')

    # Drop craft_ingredients table
    op.drop_table('craft_ingredients')

    # Drop indexes for crafts
    op.drop_index('ix_crafts_status_organization', table_name='crafts')
    op.drop_index('ix_crafts_status', table_name='crafts')
    op.drop_index('ix_crafts_requested_by', table_name='crafts')
    op.drop_index('ix_crafts_organization_id', table_name='crafts')
    op.drop_index('ix_crafts_blueprint_id', table_name='crafts')

    # Drop crafts table
    op.drop_table('crafts')


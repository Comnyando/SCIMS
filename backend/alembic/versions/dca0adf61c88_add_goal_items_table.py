"""add_goal_items_table

Revision ID: dca0adf61c88
Revises: c013d2bab528
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'dca0adf61c88'
down_revision: Union[str, None] = 'c013d2bab528'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create goal_items table
    op.create_table(
        'goal_items',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('goal_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the goal'),
        sa.Column('item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the target item'),
        sa.Column('target_quantity', sa.Numeric(precision=15, scale=3), nullable=False, comment='Target quantity for this item'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('goal_id', 'item_id', name='uq_goal_item_goal_item'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        comment='Individual target items for each goal'
    )

    # Create indexes for goal_items
    op.create_index('ix_goal_items_goal_id', 'goal_items', ['goal_id'])
    op.create_index('ix_goal_items_item_id', 'goal_items', ['item_id'])


def downgrade() -> None:
    # Drop indexes for goal_items
    op.drop_index('ix_goal_items_item_id', table_name='goal_items')
    op.drop_index('ix_goal_items_goal_id', table_name='goal_items')

    # Drop goal_items table
    op.drop_table('goal_items')


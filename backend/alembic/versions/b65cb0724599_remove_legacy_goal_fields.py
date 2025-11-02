"""remove_legacy_goal_fields

Revision ID: b65cb0724599
Revises: dca0adf61c88
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b65cb0724599'
down_revision: Union[str, None] = 'dca0adf61c88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop index for target_item_id
    op.drop_index('ix_goals_target_item_id', table_name='goals')
    
    # Drop foreign key constraint for target_item_id
    op.drop_constraint('goals_target_item_id_fkey', 'goals', type_='foreignkey')
    
    # Drop target_item_id and target_quantity columns
    op.drop_column('goals', 'target_item_id')
    op.drop_column('goals', 'target_quantity')


def downgrade() -> None:
    # Re-add columns (needed for rollback, but this is one-way migration)
    op.add_column('goals', sa.Column('target_item_id', sa.String(), nullable=True))
    op.add_column('goals', sa.Column('target_quantity', sa.Numeric(precision=15, scale=3), nullable=True))
    
    # Re-add foreign key
    op.create_foreign_key('goals_target_item_id_fkey', 'goals', 'items', ['target_item_id'], ['id'], ondelete='SET NULL')
    
    # Re-add index
    op.create_index('ix_goals_target_item_id', 'goals', ['target_item_id'])


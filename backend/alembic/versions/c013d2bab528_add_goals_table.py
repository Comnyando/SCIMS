"""add_goals_table

Revision ID: c013d2bab528
Revises: c8d7e9f0a1b2
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c013d2bab528'
down_revision: Union[str, None] = 'c8d7e9f0a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Goal name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Goal description'),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Organization this goal belongs to (nullable)'),
        sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False, comment='User who created this goal'),
        sa.Column('target_item_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Target item for this goal (nullable)'),
        sa.Column('target_quantity', sa.Numeric(precision=15, scale=3), nullable=False, comment='Target quantity to achieve'),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True, comment='Target completion date (nullable)'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active', comment='Goal status: active, completed, cancelled'),
        sa.Column('progress_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Progress tracking data (JSON)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_item_id'], ['items.id'], ondelete='SET NULL'),
        comment='Goals tracking for inventory management'
    )

    # Create indexes for goals
    op.create_index('ix_goals_organization_id', 'goals', ['organization_id'])
    op.create_index('ix_goals_created_by', 'goals', ['created_by'])
    op.create_index('ix_goals_target_item_id', 'goals', ['target_item_id'])
    op.create_index('ix_goals_status', 'goals', ['status'])
    op.create_index('ix_goals_status_organization', 'goals', ['status', 'organization_id'])
    op.create_index('ix_goals_target_date', 'goals', ['target_date'])

    # Create trigger for goals updated_at
    op.execute("""
        CREATE TRIGGER update_goals_updated_at 
        BEFORE UPDATE ON goals 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger for goals updated_at
    op.execute("DROP TRIGGER IF EXISTS update_goals_updated_at ON goals;")

    # Drop indexes for goals
    op.drop_index('ix_goals_target_date', table_name='goals')
    op.drop_index('ix_goals_status_organization', table_name='goals')
    op.drop_index('ix_goals_status', table_name='goals')
    op.drop_index('ix_goals_target_item_id', table_name='goals')
    op.drop_index('ix_goals_created_by', table_name='goals')
    op.drop_index('ix_goals_organization_id', table_name='goals')

    # Drop goals table
    op.drop_table('goals')


"""add_integrations_tables

Revision ID: e2cc834b1e72
Revises: 8c94020b6137
Create Date: 2025-11-02 21:58:09.502288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e2cc834b1e72'
down_revision: Union[str, None] = '8c94020b6137'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Integration name'),
        sa.Column('type', sa.String(length=100), nullable=False, comment='Integration type (webhook, api, etc.)'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active', comment='Integration status (active, inactive, error)'),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False, comment='User who created this integration'),
        sa.Column('organization_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Organization this integration belongs to (nullable)'),
        sa.Column('webhook_url', sa.String(length=500), nullable=True, comment='Webhook URL for receiving events'),
        sa.Column('api_key_encrypted', sa.Text(), nullable=True, comment='Encrypted API key (if applicable)'),
        sa.Column('api_secret_encrypted', sa.Text(), nullable=True, comment='Encrypted API secret (if applicable)'),
        sa.Column('config_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional configuration data (JSON)'),
        sa.Column('last_tested_at', sa.DateTime(timezone=True), nullable=True, comment='Last successful test timestamp'),
        sa.Column('last_error', sa.Text(), nullable=True, comment='Last error message (if status is error)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        comment='External integrations configuration (webhooks, APIs, etc.)'
    )
    op.create_index('ix_integrations_user_id', 'integrations', ['user_id'])
    op.create_index('ix_integrations_organization_id', 'integrations', ['organization_id'])
    op.create_index('ix_integrations_type', 'integrations', ['type'])
    op.create_index('ix_integrations_status', 'integrations', ['status'])

    # Create integration_logs table
    op.create_table(
        'integration_logs',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('integration_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the integration'),
        sa.Column('event_type', sa.String(length=100), nullable=False, comment='Type of event (test, webhook_received, error, etc.)'),
        sa.Column('status', sa.String(length=50), nullable=False, comment='Log status (success, error, pending)'),
        sa.Column('request_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Request data (JSON)'),
        sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Response data (JSON)'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message (if status is error)'),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True, comment='Execution time in milliseconds'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp of the log entry'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        comment='Logs of integration events and webhook calls'
    )
    op.create_index('ix_integration_logs_integration_id', 'integration_logs', ['integration_id'])
    op.create_index('ix_integration_logs_event_type', 'integration_logs', ['event_type'])
    op.create_index('ix_integration_logs_status', 'integration_logs', ['status'])
    op.create_index('ix_integration_logs_timestamp', 'integration_logs', ['timestamp'])

    # Create trigger to update updated_at on integrations table
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    op.execute("""
        CREATE TRIGGER update_integrations_updated_at
        BEFORE UPDATE ON integrations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_integrations_updated_at ON integrations")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop indexes for integration_logs
    op.drop_index('ix_integration_logs_timestamp', table_name='integration_logs')
    op.drop_index('ix_integration_logs_status', table_name='integration_logs')
    op.drop_index('ix_integration_logs_event_type', table_name='integration_logs')
    op.drop_index('ix_integration_logs_integration_id', table_name='integration_logs')

    # Drop integration_logs table
    op.drop_table('integration_logs')

    # Drop indexes for integrations
    op.drop_index('ix_integrations_status', table_name='integrations')
    op.drop_index('ix_integrations_type', table_name='integrations')
    op.drop_index('ix_integrations_organization_id', table_name='integrations')
    op.drop_index('ix_integrations_user_id', table_name='integrations')

    # Drop integrations table
    op.drop_table('integrations')

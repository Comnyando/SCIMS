"""add_commons_tables

Revision ID: 854d69d2dfb5
Revises: e2cc834b1e72
Create Date: 2025-11-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '854d69d2dfb5'
down_revision: Union[str, None] = 'e2cc834b1e72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Tag name (unique)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Tag description'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the tag was created'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_tags_name'),
        comment='Tags for categorizing commons entities'
    )
    op.create_index('ix_tags_name', 'tags', ['name'])

    # Create commons_submissions table
    op.create_table(
        'commons_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('submitter_id', postgresql.UUID(as_uuid=False), nullable=False, comment='User who submitted this entry'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Type of entity (item, blueprint, location, ingredient, taxonomy)'),
        sa.Column('entity_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Normalized shape for proposed entity or update (JSON)'),
        sa.Column('source_reference', sa.String(length=500), nullable=True, comment='URL or notes about the source'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='Submission status (pending, approved, rejected, needs_changes, merged)'),
        sa.Column('review_notes', sa.Text(), nullable=True, comment='Notes from moderator review'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the submission was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the submission was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submitter_id'], ['users.id'], ondelete='CASCADE'),
        comment='User submissions to the public commons'
    )
    op.create_index('ix_commons_submissions_submitter_id', 'commons_submissions', ['submitter_id'])
    op.create_index('ix_commons_submissions_entity_type', 'commons_submissions', ['entity_type'])
    op.create_index('ix_commons_submissions_status', 'commons_submissions', ['status'])
    op.create_index('ix_commons_submissions_status_created_at', 'commons_submissions', [sa.text('status'), sa.text('created_at DESC')])

    # Create commons_moderation_actions table
    op.create_table(
        'commons_moderation_actions',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('submission_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the submission'),
        sa.Column('moderator_id', postgresql.UUID(as_uuid=False), nullable=False, comment='User who performed the moderation action'),
        sa.Column('action', sa.String(length=50), nullable=False, comment='Type of action (approve, reject, request_changes, merge, edit)'),
        sa.Column('action_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Action-specific data (diffs/merge mapping)'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Notes about the action'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the action was performed'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['submission_id'], ['commons_submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='RESTRICT'),
        comment='Log of moderation actions on submissions'
    )
    op.create_index('ix_commons_moderation_actions_submission_id', 'commons_moderation_actions', ['submission_id'])
    op.create_index('ix_commons_moderation_actions_moderator_id', 'commons_moderation_actions', ['moderator_id'])
    op.create_index('ix_commons_moderation_actions_action', 'commons_moderation_actions', ['action'])

    # Create commons_entities table
    op.create_table(
        'commons_entities',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Type of entity (item, blueprint, location, ingredient, taxonomy)'),
        sa.Column('canonical_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Reference to items.id/blueprints.id/locations.id when applicable'),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Denormalized public representation (immutable snapshot per version)'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1', comment='Version number of this entity'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.false(), comment='Whether this entity is publicly visible'),
        sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False, comment='User who created this entity'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the entity was created'),
        sa.Column('superseded_by', postgresql.UUID(as_uuid=False), nullable=True, comment='Reference to the entity that superseded this one'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['superseded_by'], ['commons_entities.id'], ondelete='SET NULL'),
        comment='Published entities in the public commons'
    )
    op.create_index('ix_commons_entities_entity_type', 'commons_entities', ['entity_type'])
    op.create_index('ix_commons_entities_is_public', 'commons_entities', ['is_public'])
    op.create_index('ix_commons_entities_canonical_id', 'commons_entities', ['canonical_id'])
    op.create_index('ix_commons_entities_entity_type_is_public_version', 'commons_entities', [sa.text('entity_type'), sa.text('is_public'), sa.text('version DESC')])

    # Create commons_entity_tags table
    op.create_table(
        'commons_entity_tags',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('commons_entity_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the commons entity'),
        sa.Column('tag_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the tag'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['commons_entity_id'], ['commons_entities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('commons_entity_id', 'tag_id', name='uq_commons_entity_tags_entity_tag'),
        comment='Many-to-many relationship between commons entities and tags'
    )
    op.create_index('ix_commons_entity_tags_commons_entity_id', 'commons_entity_tags', ['commons_entity_id'])
    op.create_index('ix_commons_entity_tags_tag_id', 'commons_entity_tags', ['tag_id'])

    # Create entity_aliases table
    op.create_table(
        'entity_aliases',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Type of entity (item, blueprint, location)'),
        sa.Column('canonical_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to items.id/blueprints.id/locations.id'),
        sa.Column('alias', sa.String(length=255), nullable=False, comment='Alternative name or alias'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entity_type', 'canonical_id', 'alias', name='uq_entity_aliases_type_id_alias'),
        comment='Alternative names/aliases for entities'
    )
    op.create_index('ix_entity_aliases_entity_type', 'entity_aliases', ['entity_type'])
    op.create_index('ix_entity_aliases_canonical_id', 'entity_aliases', ['canonical_id'])
    op.create_index('ix_entity_aliases_entity_type_alias', 'entity_aliases', ['entity_type', 'alias'])

    # Create duplicate_groups table
    op.create_table(
        'duplicate_groups',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Type of entity (item, blueprint, location)'),
        sa.Column('group_key', sa.String(length=255), nullable=False, comment='Heuristic key for grouping duplicates'),
        sa.Column('members', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='List of IDs considered duplicates (JSON array)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, comment='Timestamp when the group was created'),
        sa.PrimaryKeyConstraint('id'),
        comment='Groups of entities identified as potential duplicates'
    )
    op.create_index('ix_duplicate_groups_entity_type', 'duplicate_groups', ['entity_type'])
    op.create_index('ix_duplicate_groups_group_key', 'duplicate_groups', ['group_key'])

    # Add triggers for updated_at on commons_submissions
    op.execute("""
        CREATE TRIGGER set_commons_submissions_updated_at
        BEFORE UPDATE ON commons_submissions
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS set_commons_submissions_updated_at ON commons_submissions;")

    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('duplicate_groups')
    op.drop_table('entity_aliases')
    op.drop_table('commons_entity_tags')
    op.drop_table('commons_entities')
    op.drop_table('commons_moderation_actions')
    op.drop_table('commons_submissions')
    op.drop_table('tags')

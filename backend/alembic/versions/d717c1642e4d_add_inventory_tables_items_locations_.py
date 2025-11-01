"""add_inventory_tables_items_locations_stocks_history

Revision ID: d717c1642e4d
Revises: 001_initial
Create Date: 2025-10-31 20:21:33.852712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd717c1642e4d'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Location name'),
        sa.Column('type', sa.String(length=50), nullable=False, comment='Location type: station, ship, player_inventory, warehouse'),
        sa.Column('owner_type', sa.String(length=50), nullable=False, comment='Owner type: user, organization, ship'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the owner (user, organization, or ship)'),
        sa.Column('parent_location_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Parent location for nested locations (optional)'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Flexible location-specific data (JSON)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.PrimaryKeyConstraint('id'),
        comment='Storage locations (stations, ships, player inventories, warehouses)'
    )
    op.create_index('ix_locations_name', 'locations', ['name'])
    op.create_index('ix_locations_type', 'locations', ['type'])
    op.create_index('ix_locations_owner', 'locations', ['owner_type', 'owner_id'])
    op.create_index('ix_locations_parent', 'locations', ['parent_location_id'])
    
    # Add foreign key constraint for parent_location_id (self-referential)
    op.create_foreign_key(
        'fk_locations_parent_location',
        'locations', 'locations',
        ['parent_location_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create ships table
    op.create_table(
        'ships',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Ship name'),
        sa.Column('ship_type', sa.String(length=100), nullable=True, comment='Ship type/model (e.g., Constellation, Freelancer)'),
        sa.Column('owner_type', sa.String(length=50), nullable=False, comment='Owner type: user, organization'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the owner (user or organization)'),
        sa.Column('current_location_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Current location where the ship is parked/stationed (nullable when ship is in transit)'),
        sa.Column('cargo_location_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Location representing the ship cargo grid'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Ship-specific data (JSON: cargo capacity, modules, etc.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['current_location_id'], ['locations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['cargo_location_id'], ['locations.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        comment='Ships owned by users or organizations, movable between locations'
    )
    op.create_index('ix_ships_name', 'ships', ['name'])
    op.create_index('ix_ships_ship_type', 'ships', ['ship_type'])
    op.create_index('ix_ships_owner', 'ships', ['owner_type', 'owner_id'])
    op.create_index('ix_ships_current_location', 'ships', ['current_location_id'])
    op.create_index('ix_ships_cargo_location', 'ships', ['cargo_location_id'], unique=True)
    
    # Create trigger for ships updated_at
    op.execute("""
        CREATE TRIGGER update_ships_updated_at 
        BEFORE UPDATE ON ships 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Create items table
    op.create_table(
        'items',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Item name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Item description'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='Item category'),
        sa.Column('subcategory', sa.String(length=100), nullable=True, comment='Item subcategory'),
        sa.Column('rarity', sa.String(length=50), nullable=True, comment='Item rarity level'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Game-specific attributes (JSON)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.PrimaryKeyConstraint('id'),
        comment='Item catalog (definitions/master data)'
    )
    op.create_index('ix_items_name', 'items', ['name'])
    op.create_index('ix_items_category', 'items', ['category'])
    op.create_index('ix_items_subcategory', 'items', ['subcategory'])
    op.create_index('ix_items_rarity', 'items', ['rarity'])
    
    # Create item_stocks table
    op.create_table(
        'item_stocks',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the item'),
        sa.Column('location_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the location'),
        sa.Column('quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0', comment='Available quantity (supports fractional quantities)'),
        sa.Column('reserved_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0', comment='Quantity reserved for in-progress crafts'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when stock was last updated'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=False), nullable=True, comment='Reference to the user who last updated this stock'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'location_id', name='uq_item_stock_item_location'),
        comment='Stock levels for items at specific locations'
    )
    op.create_index('ix_item_stocks_item_id', 'item_stocks', ['item_id'])
    op.create_index('ix_item_stocks_location_id', 'item_stocks', ['location_id'])
    op.create_index('ix_item_stocks_updated_by', 'item_stocks', ['updated_by'])
    
    # Create item_history table
    op.create_table(
        'item_history',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='Unique identifier (UUID)'),
        sa.Column('item_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the item'),
        sa.Column('location_id', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the location'),
        sa.Column('quantity_change', sa.Numeric(precision=15, scale=3), nullable=False, comment='Quantity change (positive for additions, negative for removals)'),
        sa.Column('transaction_type', sa.String(length=50), nullable=False, comment='Transaction type: add, remove, transfer, craft, consume'),
        sa.Column('related_craft_id', postgresql.UUID(as_uuid=False), nullable=True, comment='Reference to related craft (if applicable, nullable)'),
        sa.Column('performed_by', postgresql.UUID(as_uuid=False), nullable=False, comment='Reference to the user who performed the transaction'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the transaction occurred'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Optional notes about the transaction'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Audit trail of all inventory transactions and changes'
    )
    op.create_index('ix_item_history_item_id', 'item_history', ['item_id'])
    op.create_index('ix_item_history_location_id', 'item_history', ['location_id'])
    op.create_index('ix_item_history_transaction_type', 'item_history', ['transaction_type'])
    op.create_index('ix_item_history_performed_by', 'item_history', ['performed_by'])
    op.create_index('ix_item_history_timestamp', 'item_history', ['timestamp'])
    # Note: related_craft_id foreign key will be added in a later migration when crafts table exists
    
    # Create database function for cleaning up old item_history records
    # This function deletes records older than the specified retention period (default 30 days)
    # Can be called via: SELECT cleanup_old_item_history(30); -- 30 days retention
    op.execute("""
        CREATE OR REPLACE FUNCTION cleanup_old_item_history(retention_days INTEGER DEFAULT 30)
        RETURNS INTEGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM item_history
            WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            
            RETURN deleted_count;
        END;
        $$;
        
        COMMENT ON FUNCTION cleanup_old_item_history IS 
        'Deletes item_history records older than the specified number of days. Default retention is 30 days. Returns the number of deleted records.';
    """)


def downgrade() -> None:
    # Drop cleanup function
    op.execute('DROP FUNCTION IF EXISTS cleanup_old_item_history(INTEGER);')
    
    # Drop indexes first
    op.drop_index('ix_item_history_timestamp', table_name='item_history')
    op.drop_index('ix_item_history_performed_by', table_name='item_history')
    op.drop_index('ix_item_history_transaction_type', table_name='item_history')
    op.drop_index('ix_item_history_location_id', table_name='item_history')
    op.drop_index('ix_item_history_item_id', table_name='item_history')
    op.drop_table('item_history')
    
    op.drop_index('ix_item_stocks_updated_by', table_name='item_stocks')
    op.drop_index('ix_item_stocks_location_id', table_name='item_stocks')
    op.drop_index('ix_item_stocks_item_id', table_name='item_stocks')
    op.drop_table('item_stocks')
    
    op.drop_index('ix_items_rarity', table_name='items')
    op.drop_index('ix_items_subcategory', table_name='items')
    op.drop_index('ix_items_category', table_name='items')
    op.drop_index('ix_items_name', table_name='items')
    op.drop_table('items')
    
    # Drop ships table and its trigger
    op.execute('DROP TRIGGER IF EXISTS update_ships_updated_at ON ships;')
    op.drop_index('ix_ships_cargo_location', table_name='ships')
    op.drop_index('ix_ships_current_location', table_name='ships')
    op.drop_index('ix_ships_owner', table_name='ships')
    op.drop_index('ix_ships_ship_type', table_name='ships')
    op.drop_index('ix_ships_name', table_name='ships')
    op.drop_table('ships')
    
    # Drop foreign key constraint for parent_location_id before dropping locations table
    op.drop_constraint('fk_locations_parent_location', 'locations', type_='foreignkey')
    op.drop_index('ix_locations_parent', table_name='locations')
    op.drop_index('ix_locations_owner', table_name='locations')
    op.drop_index('ix_locations_type', table_name='locations')
    op.drop_index('ix_locations_name', table_name='locations')
    op.drop_table('locations')


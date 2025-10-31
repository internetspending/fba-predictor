"""create_base_tables

Revision ID: 47fcac774eb6
Revises:
Create Date: 2025-10-24 17:16:02.558000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '47fcac774eb6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.String(length=10), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_asin'), 'products', ['asin'], unique=True)
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)

    # Create scan_history table
    op.create_table(
        'scan_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scan_history_id'), 'scan_history', ['id'], unique=False)
    op.create_index(op.f('ix_scan_history_product_id'), 'scan_history', ['product_id'], unique=False)
    op.create_index(op.f('ix_scan_history_user_id'), 'scan_history', ['user_id'], unique=False)

    # Create saved_products table
    op.create_table(
        'saved_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_products_id'), 'saved_products', ['id'], unique=False)
    op.create_index(op.f('ix_saved_products_product_id'), 'saved_products', ['product_id'], unique=False)
    op.create_index(op.f('ix_saved_products_user_id'), 'saved_products', ['user_id'], unique=False)

    # Add foreign key constraints
    op.create_foreign_key(None, 'scan_history', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'scan_history', 'products', ['product_id'], ['id'])
    op.create_foreign_key(None, 'saved_products', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'saved_products', 'products', ['product_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint(None, 'saved_products', type_='foreignkey')
    op.drop_constraint(None, 'saved_products', type_='foreignkey')
    op.drop_constraint(None, 'scan_history', type_='foreignkey')
    op.drop_constraint(None, 'scan_history', type_='foreignkey')

    # Drop indexes
    op.drop_index(op.f('ix_saved_products_user_id'), table_name='saved_products')
    op.drop_index(op.f('ix_saved_products_product_id'), table_name='saved_products')
    op.drop_index(op.f('ix_saved_products_id'), table_name='saved_products')
    op.drop_index(op.f('ix_scan_history_user_id'), table_name='scan_history')
    op.drop_index(op.f('ix_scan_history_product_id'), table_name='scan_history')
    op.drop_index(op.f('ix_scan_history_id'), table_name='scan_history')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_index(op.f('ix_products_asin'), table_name='products')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')

    # Drop tables
    op.drop_table('saved_products')
    op.drop_table('scan_history')
    op.drop_table('products')
    op.drop_table('users')

"""create_keepa_snapshots

Revision ID: b2b2fb0035a8
Revises: 47fcac774eb6
Create Date: 2025-10-31 22:07:16.350746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2b2fb0035a8'
down_revision = '47fcac774eb6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create keepa_snapshots table
    op.create_table(
        'keepa_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False, server_default='keepa'),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_keepa_snapshots_id'), 'keepa_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_keepa_snapshots_asin'), 'keepa_snapshots', ['asin'], unique=False)
    op.create_index(op.f('ix_keepa_snapshots_created_at'), 'keepa_snapshots', ['created_at'], unique=False)
    # Composite index for common query pattern: asin + created_at DESC
    op.create_index('ix_keepa_snapshots_asin_created_at', 'keepa_snapshots', ['asin', sa.text('created_at DESC')], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_keepa_snapshots_asin_created_at', table_name='keepa_snapshots')
    op.drop_index(op.f('ix_keepa_snapshots_created_at'), table_name='keepa_snapshots')
    op.drop_index(op.f('ix_keepa_snapshots_asin'), table_name='keepa_snapshots')
    op.drop_index(op.f('ix_keepa_snapshots_id'), table_name='keepa_snapshots')
    # Drop table
    op.drop_table('keepa_snapshots')

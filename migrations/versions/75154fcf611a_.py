"""empty message

Revision ID: 75154fcf611a
Revises: d6a3437fc8d4
Create Date: 2025-03-19 18:55:56.376757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75154fcf611a'
down_revision = 'd6a3437fc8d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('appointment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointment_participants',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'appointment_id'),
    info={'bind_key': None}
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointment_participants')
    op.drop_table('appointment')
    # ### end Alembic commands ###

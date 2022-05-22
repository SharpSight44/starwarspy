"""empty message

Revision ID: c11696dcd871
Revises: 2d56a5426174
Create Date: 2022-05-21 23:46:02.415687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c11696dcd871'
down_revision = '2d56a5426174'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('user_name', sa.String(length=120), nullable=False))
    op.create_unique_constraint(None, 'user', ['user_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'user_name')
    # ### end Alembic commands ###

"""
empty message

Revision ID: 293c96c33c17
Revises: 09cced627ac9
Create Date: 2019-10-02 11:28:11.237528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '293c96c33c17'
down_revision = '09cced627ac9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('csv_file', sa.Column('selected_columns', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('csv_file', 'selected_columns')
    # ### end Alembic commands ###
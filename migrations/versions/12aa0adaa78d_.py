"""empty message

Revision ID: 12aa0adaa78d
Revises: 835b6f637d98
Create Date: 2023-07-13 23:51:43.049439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "12aa0adaa78d"
down_revision = "835b6f637d98"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("confirmed_at", sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("confirmed_at")

    # ### end Alembic commands ###

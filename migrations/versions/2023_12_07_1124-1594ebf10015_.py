"""empty message

Revision ID: 1594ebf10015
Revises: d0551f9f68ce
Create Date: 2023-12-07 11:24:54.917458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1594ebf10015"
down_revision = "d0551f9f68ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("entry", schema=None) as batch_op:
        batch_op.drop_column("encrypted")
    with op.batch_alter_table("role", schema=None) as batch_op:
        batch_op.alter_column(
            "description", existing_type=sa.VARCHAR(length=255), nullable=True
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("entry", schema=None) as batch_op:
        batch_op.add_column(sa.Column("encrypted", sa.BOOLEAN(), nullable=False))
    with op.batch_alter_table("role", schema=None) as batch_op:
        batch_op.alter_column(
            "description", existing_type=sa.VARCHAR(length=255), nullable=False
        )
    # ### end Alembic commands ###

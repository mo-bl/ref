"""Add rebuild_counter columns to Exercise and Instance

Tracks atomic-rebuild generations so an instance whose snapshotted counter
falls behind its exercise's counter can be redeployed on the next connect.

Revision ID: f8a0c2d4e6b8
Revises: e6f8a0b1c3d4
Create Date: 2026-04-30

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f8a0c2d4e6b8"
down_revision = "e6f8a0b1c3d4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("exercise", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "rebuild_counter",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

    with op.batch_alter_table("exercise_instance", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "rebuild_counter",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )


def downgrade():
    with op.batch_alter_table("exercise_instance", schema=None) as batch_op:
        batch_op.drop_column("rebuild_counter")

    with op.batch_alter_table("exercise", schema=None) as batch_op:
        batch_op.drop_column("rebuild_counter")

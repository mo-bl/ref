"""Add REBUILDING value to ExerciseBuildStatus enum

REBUILDING distinguishes an atomic rebuild over an already-built exercise
(canonical image tag still serves the previous-good image) from a regular
BUILDING (no image at all). The two cases require different handling on
crash recovery, scoreboard online filtering, and admin-UI gating.

Revision ID: e6f8a0b1c3d4
Revises: d5e7f9a0b1c2
Create Date: 2026-04-30

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "e6f8a0b1c3d4"
down_revision = "d5e7f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL 12+ allows ADD VALUE inside a transaction. The value must
    # not be referenced in the same transaction that adds it; we never do
    # that here.
    op.execute("ALTER TYPE exercisebuildstatus ADD VALUE IF NOT EXISTS 'REBUILDING'")


def downgrade():
    # PostgreSQL has no DROP VALUE for enums. Reverting requires recreating
    # the enum type, which is not worth the complexity for an additive
    # migration. Any rows still using REBUILDING would also need to be
    # rewritten first. Leave as a no-op.
    pass

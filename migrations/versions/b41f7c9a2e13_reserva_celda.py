"""Agrega la celda elegida a las reservas

Flujo original: el usuario podía escoger una celda en el mapa al reservar,
pero la tabla `reservas` no tenía la columna `celda_id`, así que el servicio
fallaba con "has no property 'celda_id'". Esta migración la agrega.

Revision ID: b41f7c9a2e13
Revises: 802ed3753fc4
Create Date: 2026-11-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b41f7c9a2e13'
down_revision = '802ed3753fc4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reservas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('celda_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_reservas_celda_id_celdas',
            'celdas',
            ['celda_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('reservas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_reservas_celda_id_celdas', type_='foreignkey')
        batch_op.drop_column('celda_id')

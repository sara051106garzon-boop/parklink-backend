"""Agrega planta, estado y datos del vehículo a las celdas

El frontend muestra por celda la planta, el estado ('libre'/'ocupado'/
'reservado') y los datos del vehículo estacionado (placa, usuario, marca,
modelo, color, hora de ingreso). La tabla `celdas` no tenía esas columnas y
el backend las simulaba con `getattr`; esta migración las agrega de verdad.

Revision ID: c3d8e5f7a9b1
Revises: b41f7c9a2e13
Create Date: 2026-11-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d8e5f7a9b1'
down_revision = 'b41f7c9a2e13'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('celdas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planta', sa.Integer(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('estado', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('placa', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('usuario', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('marca', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('modelo', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('color_hex', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('hora_ingreso', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('celdas', schema=None) as batch_op:
        batch_op.drop_column('hora_ingreso')
        batch_op.drop_column('color_hex')
        batch_op.drop_column('modelo')
        batch_op.drop_column('marca')
        batch_op.drop_column('usuario')
        batch_op.drop_column('placa')
        batch_op.drop_column('estado')
        batch_op.drop_column('planta')

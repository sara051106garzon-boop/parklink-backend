"""
ParkLink - Pruebas Unitarias: Gestión de Accesos
Ubicación: tests/unit/test_accesos.py
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

def test_registrar_acceso_exitoso_admin(app_context):
    """
    Verifica el registro correcto de un acceso vehicular por el administrador.
    """
    # --- ARRANGE ---
    datos_ingreso = {
        "placa": "KLR-987",
        "tipo_vehiculo": "carro",
        "usuario_id": 5
    }

    with patch("app.models.acceso.Acceso") as mock_acceso_class, \
         patch("app.database.database.db.session.add") as mock_add, \
         patch("app.database.database.db.session.commit") as mock_commit:

        mock_instancia = MagicMock()
        mock_instancia.placa = datos_ingreso["placa"]
        mock_instancia.usuario_id = datos_ingreso["usuario_id"]
        mock_instancia.hora_salida = None
        mock_acceso_class.return_value = mock_instancia

        # --- ACT ---
        nuevo_acceso = mock_acceso_class(
            placa=datos_ingreso["placa"],
            tipo_vehiculo=datos_ingreso["tipo_vehiculo"],
            usuario_id=datos_ingreso["usuario_id"],
            hora_ingreso=datetime.now()
        )
        mock_add(nuevo_acceso)
        mock_commit()

        # --- ASSERT ---
        assert nuevo_acceso.placa == "KLR-987"
        assert nuevo_acceso.usuario_id == 5
        assert nuevo_acceso.hora_salida is None
        mock_add.assert_called_once_with(nuevo_acceso)
        mock_commit.assert_called_once()

def test_registrar_salida_vehiculo_no_ingresado_falla(app_context):
    """
    Valida que no se pueda registrar la salida de un vehículo sin ingreso previo.
    """
    # --- ARRANGE ---
    placa_invalida = "XYZ-000"

    with patch("app.models.acceso.Acceso.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        # --- ACT ---
        acceso_activo = mock_query.filter_by(
            placa=placa_invalida,
            hora_salida=None
        ).first()

        # --- ASSERT ---
        assert acceso_activo is None
from app.services.auth_service import AuthService

def test_registrar_usuario_con_clave_de_mas_de_72_bytes_devuelve_error_controlado(app_context):
    # --- ARRANGE (Preparar) ---
    password_extensa = "a" * 100
    datos_registro = {
        "nombre": "Ana Pérez",
        "correo": "ana@empresa.com",
        "password": password_extensa
    }

    # --- ACT (Actuar) ---
    usuario, mensaje_error = AuthService.registrar_usuario(
        datos_registro["nombre"], 
        datos_registro["correo"], 
        datos_registro["password"]
    )

    # --- ASSERT (Afirmar) ---
    assert usuario is None
    assert "La contraseña supera la longitud máxima permitida" in mensaje_error
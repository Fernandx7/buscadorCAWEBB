from werkzeug.security import check_password_hash, generate_password_hash


USUARIO = {
    "Marcella": generate_password_hash("@Marcella2025"),
    "Fernando": generate_password_hash("@Fernando0000"),
}

API_URL = "http://131.163.96.121:8000/buscar?codigo_rastreio="
CA_API_URL = "http://131.163.96.121:8000/buscar_ca?"
URL_CEP = "http://131.163.96.121:8000/Buscar_cep?cep="


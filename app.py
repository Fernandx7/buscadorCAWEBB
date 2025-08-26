from flask import Flask, render_template, request, redirect, url_for, session
import requests
import re
from datetime import datetime
from werkzeug.security import check_password_hash
from users import USUARIO, API_URL, CA_API_URL, URL_CEP

mensagemErro = "Desculpe, parece que o Servidor está offline, por favor me mande mensagem!"
app = Flask(__name__)
app.secret_key = "chave"

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if usuario in USUARIO and check_password_hash(USUARIO[usuario], senha):
            session["usuario"] = usuario
            return redirect(url_for("index"))
        else:
            erro = "Usuário ou senha incorretos."
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

def login_requerido(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def root():
    return redirect(url_for("login"))

@app.route("/individual", methods=["GET", "POST"])
@login_requerido
def index():
    resultado = None
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip().upper()
        if codigo:
            try:
                response = requests.get(API_URL, params={"codigo_rastreio": codigo})
                data = response.json()
                if "encontrado_em" in data and data["encontrado_em"]:
                    resultado = data["encontrado_em"][0]
                else:
                    resultado = "not_found"
            except Exception as e:
                # resultado = f"erro: {e}"
                resultado = f"erro: {mensagemErro}"
    return render_template("index.html", resultado=resultado)

@app.route("/lote", methods=["GET", "POST"])
@login_requerido
def lote():
    resultados = []
    if request.method == "POST":
        codigos = request.form.get("codigos", "").strip().upper().splitlines()
        codigos_validos = [c for c in codigos if re.match(r"^[A-Z]{2}\d{9}BR$", c)]

        for codigo in codigos_validos:
            try:
                response = requests.get(API_URL, params={"codigo_rastreio": codigo})
                data = response.json()
                if "encontrado_em" in data and data["encontrado_em"]:
                    resultados.append((codigo, data["encontrado_em"][0], None))
                else:
                    resultados.append((codigo, None, "NÃO ENCONTRADO"))
            except Exception as resultado:
                resultado = f"erro: {mensagemErro}"
    return render_template("lote.html", resultados=resultados)

@app.route("/ca", methods=["GET", "POST"])
@login_requerido
def ca():
    resultados = []
    erro = None
    data_str = ""
    if request.method == "POST":
        data_str = request.form.get("data", "")
        try:
            data_obj = datetime.strptime(data_str, "%Y-%m-%d")
            if data_obj.weekday() >= 5:
                erro = "A data selecionada é um fim de semana."
            else:
                data_formatada = data_obj.strftime("%d/%m/%Y")
                response = requests.get(CA_API_URL, params={"data": data_formatada})
                data = response.json()
                encontrados = data.get("resultados", [])
                if encontrados: 
                    resultados = encontrados 
                else: 
                    erro = "objetos não encontrados na data especificada."
        except ValueError:
            erro = "Formato de data inválido."
        except Exception as erro:
            erro = f"{mensagemErro}"
    return render_template("ca.html", resultados=resultados, erro=erro, data_str=data_str)


@app.route("/Buscar_cep", methods=["GET", "POST"])
@login_requerido
def buscar_cep():
    resultados = []
    erro = None
    cep = ""

    if request.method == "POST":
        cep = request.form.get("cep", "").strip()
        if not (cep.isdigit() and len(cep) == 8):
            erro = "CEP inválido. O CEP deve conter 8 dígitos."
        else:
            try:
                response = requests.get(URL_CEP, params={"cep": cep})
                data = response.json()
                if "Encontrados" in data and data["Encontrados"]:
                    resultados = data["Encontrados"]
                else:
                    erro = "CEP não encontrado."
            except Exception as e:
                erro = mensagemErro

    return render_template("buscar_cep.html", resultados=resultados, erro=erro, cep=cep)

if __name__ == "__main__":
    app.run(debug=True)

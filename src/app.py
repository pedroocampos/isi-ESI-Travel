from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from amadeus import Client, ResponseError
from vuelo import Vuelo


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

amadeus = Client(
    client_id='H8Ci5KBBxNg7dGQ5gScDxk6feM8IGYwd',
    client_secret='Oe9kxiuyw6ORXZVW'
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(80))
    email = db.Column(db.String(100))

@app.route("/")
def home():
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

@app.route("/busqueda", methods=["GET", "POST"])
def buscar_vuelo():
    parada = request.form.get("checkVueloDirecto")
    if parada == "on":
        parada = "true"
    else:
        parada = "false"

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=str(request.form["inputOrigen"]),
            destinationLocationCode=str(request.form["inputDestino"]),
            departureDate=str(request.form.get("inputFechaSalida")),
            adults=str(request.form["inputAdultos"]),
            children=str(request.form["inputNiños"]),
            infants=str(request.form["inputBebes"]),
            nonStop=parada
        )
    except ResponseError as error_msg:
        print(error_msg)

    lista_vuelos = []
    for i in range(len(response.data) - 1):
        vuelo = Vuelo(
            id = response.data[i]['id'],
            origen = response.data[i]['itineraries'][0]['segments'][0]['departure']['iataCode'],
            destino = response.data[i]['itineraries'][0]['segments'][0]['arrival']['iataCode'],
            fecha = response.data[i]['itineraries'][0]['segments'][0]['departure']['at'][0:10],
            horaSalida = response.data[i]['itineraries'][0]['segments'][0]['departure']['at'][11:16],
            horaLlegada = response.data[i]['itineraries'][0]['segments'][0]['arrival']['at'][11:16],
            compania = response.data[i]['itineraries'][0]['segments'][0]['carrierCode'],
            paradas = response.data[i]['itineraries'][0]['segments'][0]['numberOfStops'],
            precio = response.data[i]['price']['total'],
            asientosDisponibles = response.data[i]['numberOfBookableSeats']
        )
        lista_vuelos.append(vuelo)

    return render_template("index.html", vuelos=lista_vuelos, accion="Iniciar sesión", metodo_accion="iniciar_sesion")


@app.route("/login")
def iniciar_sesion():
    return render_template("login.html")

@app.route("/")
def cerrar_sesion():
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

@app.route("/login", methods=["POST"])
def comprobar_usuario():
    correo_electronico = request.form["email_login"]
    contraseña = request.form["contraseña_login"]

    usuario = User.query.filter(User.email == correo_electronico, User.password == contraseña).first()
    if not usuario:
        return render_template("login.html", error="Correo electrónico o contraseña incorrecto")
    else:
        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/registro")
def registrar():
    return render_template("registro.html")

@app.route("/registro", methods=["POST"])
def insertar_usuario():
    usuario = User(
        username = request.form["nombre_usuario_registro"],
        password = request.form["contraseña_registro"],
        email = request.form["email_registro"]
    )

    usuario_registrado = User.query.filter(User.email == usuario.email, User.username == usuario.username, User.password == usuario.password).first()
    if not usuario_registrado:
        db.session.add(usuario)
        db.session.commit()
        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return render_template("registro.html", error="El usuario ya está registrado")

if __name__ == "__main__":
    app.run(debug=True)
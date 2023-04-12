from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from amadeus import Client, ResponseError
from vuelo import Vuelo
from hotel import Hotel


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

amadeus = Client(
    client_id='36eTUH6WOGQlrOkjeKr4K8QOVXNJe0iu',
    client_secret='yI0mSUcRFgkLlaGs'
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(80))
    email = db.Column(db.String(100))

lista_vuelos = []
lista_hoteles = []
usuario_activo = {
    "correo": None,
    "nombre_usuario": None,
    "password": None
}
reserva = {
    "vuelo": None,
    "usuario": None,
    "hotel": None
}
pasajeros_total = None
fecha_llegada = None

@app.route("/")
def home():
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

@app.route("/login")
def iniciar_sesion():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def comprobar_usuario():
    correo_electronico = request.form["email_login"]
    contraseña = request.form["contraseña_login"]

    usuario = User.query.filter(User.email == correo_electronico, User.password == contraseña).first()
    if not usuario:
        return render_template("login.html", error="Correo electrónico o contraseña incorrecto")
    else:
        usuario_activo["correo"] = usuario.email
        usuario_activo["nombre_usuario"] = usuario.username
        usuario_activo["password"] = usuario.password

        if reserva["vuelo"]:
            return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    usuario_activo["correo"] = None
    usuario_activo["nombre_usuario"] = None
    usuario_activo["password"] = None
    reserva["vuelo"] = None
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

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
        usuario_activo["correo"] = usuario_registrado.email
        usuario_activo["nombre_usuario"] = usuario_registrado.username
        usuario_activo["password"] = usuario_registrado.password
        db.session.add(usuario)
        db.session.commit()

        if reserva["vuelo"]:
            return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return render_template("registro.html", error="El usuario ya está registrado")

@app.route("/busqueda/vuelos", methods=["GET", "POST"])
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

    # Aqui va la asignacio de los pasajeros y la fecha de llegada

    lista_vuelos.clear()

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

        #if pasajeros_total > vuelo.asientosDisponibles:
        #    continue
        #else:
        lista_vuelos.append(vuelo)

        # TODO: Encontrar la forma de que si se ha hecho una busqueda y se hace un render_template de index.html no se borre la busqueda

    if not usuario_activo["correo"]:
        return render_template("index.html", vuelos=lista_vuelos, accion="Iniciar sesión", metodo_accion="iniciar_sesion")

    return render_template("index.html", vuelos=lista_vuelos, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/reservar/<int:numero_vuelo>")
def reservar_vuelo(numero_vuelo):
    reserva["vuelo"] = lista_vuelos[numero_vuelo - 1]

    buscar_hoteles()

    if not usuario_activo["correo"]:
        return render_template("login.html")

    return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")


@app.route("/reservar/<int:numero_vuelo>", methods=["GET", "POST"])
def buscar_hoteles():
    hoteles_ciudad = []
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode = reserva["vuelo"].destino,
        )

        for i in range(0, len(response.data)):
            hoteles_ciudad.append(response.data[i]['hotelId'])

        response_ids = amadeus.shopping.hotel_offers_search.get(
            hotelIds = hoteles_ciudad,
            checkInDate = str(reserva["vuelo"].fecha),
            checkOutDate = str(fecha_llegada),
            adults = int(pasajeros_total) # TODO: Mirar porque los pasajeros se quedan a None
        )

        for i in range(len(response_ids.data) - 1):
            hotel = Hotel(
                id = response_ids.data[i]['hotelId'],
                nombre = response_ids.data[i]['name'],
                ubicacion= response_ids.data[i]['address']['cityName'],
                estrellas = response_ids.data[i]["offers"][0]["hotel"]["rating"],
                precio = response_ids.data[i]["offers"][0]["price"]["total"],
                fechaSalida = response_ids.data[i]["offers"][0]["price"]["checkOutDate"],
                fechaEntrada = response_ids.data[i]["offers"][0]["price"]["checkInDate"],
                disponibilidad= response_ids.data[i]["offers"][0]["available"]
            )

            lista_hoteles.append(hotel)

    except ResponseError as error_msg:
        print(error_msg)



if __name__ == "__main__":
    app.run(debug=True)
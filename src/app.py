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
    "hotel": None
}

pasajeros_total = None
fecha_llegada = None
buscar_alojamiento = True

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

        if reserva["vuelo"] and not buscar_alojamiento:
            terminar_reserva("", 0)
        elif reserva["vuelo"] and buscar_alojamiento:
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
        usuario_activo["correo"] = usuario.email
        usuario_activo["nombre_usuario"] = usuario.username
        usuario_activo["password"] = usuario.password
        db.session.add(usuario)
        db.session.commit()

        if reserva["vuelo"] and not buscar_alojamiento:
            terminar_reserva("", 0)
        elif reserva["vuelo"] and buscar_alojamiento:
            return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return render_template("registro.html", error="El usuario ya está registrado")

@app.route("/reservar/confirmar", methods=["GET"])
def terminar_reserva(hotel, precio_hotel): # TODO: Resolver este error TypeError: terminar_reserva() missing 2 required positional arguments: 'hotel' and 'precio_hotel'
    precio_reserva = reserva["vuelo"].precio
    ocultar_etiquetas = True

    if hotel != "":
        precio_reserva = reserva["vuelo"].precio + precio_hotel
        ocultar_etiquetas = False

    return render_template("reserva.html",
                           correo_electronico = usuario_activo["correo"],
                           vuelo = reserva["vuelo"].origen + " -> " + reserva["vuelo"].destino,
                           hora_salida = reserva["vuelo"].horaSalida,
                           hora_llegada = reserva["vuelo"].horaLlegada,
                           nombre_hotel = hotel,
                           precio = precio_reserva,
                           ocultar_etiquetas=ocultar_etiquetas
            )

@app.route("/busqueda/vuelos", methods=["GET", "POST"])
def buscar_vuelo():
    global buscar_alojamiento
    parada = request.form.get("checkBuscarAlojamiento")
    vuelta = request.form.get("checkVuelta")
    buscar_vuelta = True
    vuelos_vuelta = []
    
    if parada != "on":
        buscar_alojamiento = False

    if vuelta != "on":
        buscar_vuelta = False
        
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=str(request.form["inputOrigen"]),
            destinationLocationCode=str(request.form["inputDestino"]),
            departureDate=str(request.form.get("inputFechaSalida")),
            adults=str(request.form["inputAdultos"]),
            children=str(request.form["inputNiños"]),
            infants=str(request.form["inputBebes"]),
            nonStop="true"
        )

    except ResponseError as error_msg:
        print(error_msg)

    global pasajeros_total, fecha_llegada
    pasajeros_total = int(request.form["inputAdultos"]) + int(request.form["inputNiños"]) + int(request.form["inputBebes"])
    fecha_llegada = str(request.form.get("inputFechaLlegada"))

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

        lista_vuelos.append(vuelo)

    if buscar_vuelta:
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=str(request.form["inputDestino"]),
                destinationLocationCode=str(request.form["inputOrigen"]),
                departureDate=str(request.form.get("inputFechaLlegada")),
                adults=str(request.form["inputAdultos"]),
                children=str(request.form["inputNiños"]),
                infants=str(request.form["inputBebes"]),
                nonStop="true"
            )

        except ResponseError as error_msg:
            print(error_msg)

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
            vuelos_vuelta.append(vuelo)
            
    
    if not usuario_activo["correo"]:
        return render_template("index.html", vuelos=lista_vuelos, vuelos_vuelta=vuelos_vuelta, accion="Iniciar sesión", metodo_accion="iniciar_sesion")

    return render_template("index.html", vuelos=lista_vuelos, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/reservar/<int:numero_vuelo>")
def reservar_vuelo(numero_vuelo):
    reserva["vuelo"] = lista_vuelos[numero_vuelo - 1]

    if not usuario_activo["correo"]:
        return render_template("login.html")

    if buscar_alojamiento:
        buscar_hoteles()
        return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    terminar_reserva("", 0)


@app.route("/reservar/<int:numero_vuelo>", methods=["GET", "POST"])
def buscar_hoteles():
    hoteles_ciudad = []
    global pasajeros_total, fecha_llegada

    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode = reserva["vuelo"].destino,
        )

        for i in range(0, len(response.data) - 1):
            hoteles_ciudad.append(response.data[i]['hotelId'])

        response_ids = amadeus.shopping.hotel_offers_search.get(
            hotelIds = hoteles_ciudad,
            checkInDate = str(reserva["vuelo"].fecha),
            checkOutDate = str(fecha_llegada),
            adults = pasajeros_total
        )

        for i in range(len(response_ids.data) - 1):
            hotel = Hotel(
                id = response_ids.data[i]["hotel"]['hotelId'],
                nombre = response_ids.data[i]["hotel"]['name'],
                precio = response_ids.data[i]["offers"][0]["price"]["total"],
                fechaSalida = response_ids.data[i]["offers"][0]["checkOutDate"],
                fechaEntrada = response_ids.data[i]["offers"][0]["checkInDate"],
            )

            lista_hoteles.append(hotel)
    except ResponseError as error_msg:
        print(error_msg)



if __name__ == "__main__":
    app.run(debug=True)
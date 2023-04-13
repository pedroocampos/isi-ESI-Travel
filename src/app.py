from flask import Flask, render_template, request, jsonify, make_response
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
vuelos_vuelta = []
lista_hoteles = []
usuario_activo = {
    "correo": None,
    "nombre_usuario": None,
    "password": None
}
reserva = {
    "vuelo_ida": None,
    "vuelo_vuelta": None,
    "hotel": None
}

pasajeros_total = None
presupuestoMax = None
fecha_llegada = None
buscar_alojamiento = True
buscar_vuelta = True

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

        if reserva["vuelo_ida"] and not buscar_alojamiento:
            terminar_reserva(hotel="", precio_hotel=0)
        elif reserva["vuelo_ida"] and buscar_alojamiento:
            return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    usuario_activo["correo"] = None
    usuario_activo["nombre_usuario"] = None
    usuario_activo["password"] = None
    reserva["vuelo_ida"] = None
    reserva["vuelo_vuelta"] = None
    reserva["hotel"] = None
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

        if reserva["vuelo_ida"] and not buscar_alojamiento:
            terminar_reserva(hotel="", precio_hotel=0)
        elif reserva["vuelo_ida"] and buscar_alojamiento:
            return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return render_template("registro.html", error="El usuario ya está registrado")

@app.route("/reservar/confirmar/<hotel>/<precio_hotel>", methods=["GET"])
def terminar_reserva(hotel, precio_hotel):
    precio_reserva = float(reserva["vuelo_ida"].precio)
    ocultar_etiquetas = True
    ocultar_vuelta = True

    if hotel != "":
        precio_reserva = float(reserva["vuelo_ida"].precio) + float(precio_hotel)
        ocultar_etiquetas = False

    if reserva["vuelo_vuelta"] != None:
        precio_reserva += float(reserva["vuelo_vuelta"].precio)
        ocultar_vuelta = False
        return render_template("reserva.html",
                           correo_electronico = usuario_activo["correo"],
                           vuelo_ida = reserva["vuelo_ida"].origen + " -> " + reserva["vuelo_ida"].destino,
                           hora_salida_ida = reserva["vuelo_ida"].horaSalida,
                           hora_llegada_ida = reserva["vuelo_ida"].horaLlegada,
                           vuelo_vuelta = reserva["vuelo_vuelta"].origen + " -> " + reserva["vuelo_vuelta"].destino,
                           hora_salida_vuelta = reserva["vuelo_vuelta"].horaSalida,
                           hora_llegada_vuelta = reserva["vuelo_vuelta"].horaLlegada,
                           nombre_hotel = hotel,
                           precio = precio_reserva,
                           ocultar_vuelta = ocultar_vuelta,
                           ocultar_etiquetas = ocultar_etiquetas
            )
    return render_template("reserva.html",
                        correo_electronico = usuario_activo["correo"],
                        vuelo_ida = reserva["vuelo_ida"].origen + " -> " + reserva["vuelo_ida"].destino,
                        hora_salida_ida = reserva["vuelo_ida"].horaSalida,
                        hora_llegada_ida = reserva["vuelo_ida"].horaLlegada,
                        nombre_hotel = hotel,
                        precio = precio_reserva,
                        ocultar_vuelta = ocultar_vuelta,
                        ocultar_etiquetas = ocultar_etiquetas
        )


@app.route("/busqueda/vuelos", methods=["GET", "POST"])
def buscar_vuelo():
    global buscar_alojamiento, buscar_vuelta
    parada = request.form.get("checkBuscarAlojamiento")
    vuelta = request.form.get("checkVuelta")
    buscar_vuelta = True

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

    global pasajeros_total, fecha_llegada, presupuestoMax
    pasajeros_total = int(request.form["inputAdultos"]) + int(request.form["inputNiños"]) + int(request.form["inputBebes"])
    fecha_llegada = str(request.form.get("inputFechaLlegada"))
    presupuestoMax = float(request.form["inputDinero"]) * pasajeros_total

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
        if float(vuelo.precio) < presupuestoMax:
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
            if float(vuelo.precio) < presupuestoMax:
                vuelos_vuelta.append(vuelo)


    if not usuario_activo["correo"]:
        return render_template("index.html", vuelos=lista_vuelos, vuelos_vuelta=vuelos_vuelta, accion="Iniciar sesión", metodo_accion="iniciar_sesion")

    return render_template("index.html", vuelos=lista_vuelos, vuelos_vuelta=vuelos_vuelta, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/reservar/<int:numero_vuelo>")
def reservar_vuelo(numero_vuelo):
    global buscar_alojamiento, lista_hoteles, presupuestoMax, pasajeros_total
    print(pasajeros_total)
    print(presupuestoMax)
    reserva["vuelo_ida"] = lista_vuelos[numero_vuelo - 1]
    print((float(reserva["vuelo_ida"].precio)))
    presupuestoMax = presupuestoMax - (float(reserva["vuelo_ida"].precio))   #TODO: NO SE SI EL PASAJERO TOTAL ES NECESARIO, NO SE SI EL PRECIO SERA POR PERSONA O EN TOTAL
    print(presupuestoMax)

    if buscar_vuelta == True:
        reserva["vuelo_vuelta"] = vuelos_vuelta[numero_vuelo - 1]
        presupuestoMax = presupuestoMax - (float(reserva["vuelo_vuelta"].precio))

    buscar_hoteles()

    if not usuario_activo["correo"]:
        return render_template("login.html")

    print("Antes de buscar hoteles")
    if buscar_alojamiento:
        print("Buscando hoteles...")
        return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return(terminar_reserva(hotel="", precio_hotel=0))


@app.route("/reservar/<int:numero_vuelo>", methods=["GET", "POST"])
def buscar_hoteles():
    hoteles_ciudad = []
    global lista_hoteles, pasajeros_total, fecha_llegada, presupuestoMax

    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode = reserva["vuelo_ida"].destino,
        )

        for i in range(0, len(response.data) - 1):
            hoteles_ciudad.append(response.data[i]['hotelId'])

        response_ids = amadeus.shopping.hotel_offers_search.get(
            hotelIds = hoteles_ciudad,
            checkInDate = str(reserva["vuelo_ida"].fecha),
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
            if float(hotel.precio) <= presupuestoMax:
                lista_hoteles.append(hotel)

    except ResponseError as error_msg:
        print(error_msg)



if __name__ == "__main__":
    app.run(debug=True)
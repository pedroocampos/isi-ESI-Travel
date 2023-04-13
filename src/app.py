from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from amadeus import Client, ResponseError
from vuelo import Vuelo
from hotel import Hotel

'''
    Class Name: app.py
    Author/s name: Raul Calzado Olmo, Pedro Campos Castellanos, Raúl González Velázquez
    Release/Creation date: 13/04/2023
    Class description: Clase principal de la aplicación web de búsqueda de vuelos
'''

''' Se configura la aplicación Flask '''
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

''' Se introduce la clave de la API de Amadeus '''''
amadeus = Client(
    client_id='36eTUH6WOGQlrOkjeKr4K8QOVXNJe0iu',
    client_secret='yI0mSUcRFgkLlaGs'
    )

class User(db.Model):
    '''
    Class Name: Users
    Author/s name: Raul Calzado Olmo, Pedro Campos Castellanos, Raúl González Velázquez
    Release/Creation date: 13/04/2023
    Class description: Representa a los usuarios de la aplicación y se almacenan en la base de datos
    '''
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(80))
    email = db.Column(db.String(100))

'''Declaración de variables globales'''
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
    '''
    Method name: home
	Description of the Method: Muestra la página principal de la aplicación web.
    Return values: La página principal de la aplicación web.
    '''
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

@app.route("/login")
def iniciar_sesion():
    '''
    Method name: iniciar_sesion
	Description of the Method: Muestra la página de inicio de sesión.
    Return values: La página de inicio de sesión.
    '''
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def comprobar_usuario():
    '''
    Method name: comprobar_usuario
	Description of the Method: Hace una consulta a la base de datos para comprobar si el usuario
    existe y si la contraseña es correcta. Si es así, muestra la página principal de la aplicación o
    o la de hoteles si se encuentra en ese paso,si no, muestra la página de inicio de sesión con un
    mensaje de error.
    Return values: La página de inicio de sesión con mensaje de error, la página principal o la
    página de hoteles.
    '''
    global buscar_alojamiento
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
            return(terminar_reserva(hotel="", precio_hotel=0))
        elif reserva["vuelo_ida"] and buscar_alojamiento:
            return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/cerrar_sesion")
def cerrar_sesion():
    '''
    Method name: cerrar_sesion
	Description of the Method: Muestra la página de principal de la aplicación web y pone los valores
    de las variables globales a su valor inicial.
    Return values: La página principal de la aplicación web.
    '''
    global lista_vuelos,vuelos_vuelta,lista_hoteles,usuario_activo,reserva,pasajeros_total,presupuestoMax,fecha_llegada,buscar_alojamiento,buscar_vuelta
    lista_vuelos = []
    vuelos_vuelta = []
    lista_hoteles = []
    usuario_activo["correo"] = None
    usuario_activo["nombre_usuario"] = None
    usuario_activo["password"] = None
    reserva["vuelo_ida"] = None
    reserva["vuelo_vuelta"] = None
    reserva["hotel"] = None
    pasajeros_total = None
    presupuestoMax = None
    fecha_llegada = None
    buscar_alojamiento = True
    buscar_vuelta = True
    return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion")

@app.route("/registro")
def registrar():
    '''
    Method name: registrar
	Description of the Method: Muestra la página de registro.
    Return values: La página de registro.
    '''
    return render_template("registro.html")

@app.route("/registro", methods=["POST"])
def insertar_usuario():
    '''
    Method name: insertar_usuario
	Description of the Method: Hace una consulta a la base de datos para comprobar si el usuario
    existe. Si no existe, lo inserta en la base de datos y muestra la página principal de la aplicación
    o la de hoteles si se encuentra en ese paso, si existe, muestra la página de registro con un mensaje
    de error.
    Return values: La página de registro con mensaje de error, la página principal o la página de hoteles.
    '''
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
    '''
    Method name: terminar_reserva
	Description of the Method: Comprueba el estado de los botones de la página index.html, calcula el
    precio de la reserva teniendo en cuenta si se han buscado hoteles y vuelos de vuelta y muestra la
    página de reserva con la información correspondiente.
    Return values: Página de reserva.
    '''
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
    '''
    Method name: buscar_vuelo
	Description of the Method: busca vuelos en la API de Amadeus en función de lo introducido por el
    usuario en la página index.html y muestra la página con los resultados, ya sea con o sin vuelos 
    de vuelta.
    Return values: La página index.html con los resultados de vuelos correspondientes. 
    '''
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
    vuelos_vuelta.clear()

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

    if not lista_vuelos and not usuario_activo["correo"]:
        return render_template("index.html", accion="Iniciar sesión", metodo_accion="iniciar_sesion", error = "No se han encontrado vuelos.")
    elif not lista_vuelos and usuario_activo["correo"]:
        return render_template("index.html", accion="Cerrar sesión", metodo_accion="cerrar_sesion", error = "No se han encontrado vuelos.")


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

    vuelos_vuelta.clear()
    if not usuario_activo["correo"]:
        return render_template("index.html", vuelos=lista_vuelos, vuelos_vuelta=vuelos_vuelta, accion="Iniciar sesión", metodo_accion="iniciar_sesion")

    return render_template("index.html", vuelos=lista_vuelos, vuelos_vuelta=vuelos_vuelta, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

@app.route("/reservar/<int:numero_vuelo>")
def reservar_vuelo(numero_vuelo):
    '''
    Method name: reservar_vuelo
	Description of the Method: Almacena en reserva el vuelo seleccionado por el usuario, comprueba
    si también hay vuelo de vuelta para almacenarlo. Si el usuario no está logueado, se le redirige
    a la página de login. Si el usuario está logueado y se ha marcado la búsqueda de alojamiento, se
    le redirige a la página de hoteles. Se redirigirá a la página de terminar de reservar si no se
    ha marcado la opción de búsqueda de alojamiento.
    Return values: La página de login si el usuario no está logueado, la página de hoteles si el usuario
    lo está y se ha marcado la búsqueda de alojamiento, la página de terminar de reserva si no se
    busca alojamiento.
    '''
    global buscar_alojamiento, lista_hoteles, presupuestoMax, pasajeros_total
    reserva["vuelo_ida"] = lista_vuelos[numero_vuelo - 1]
    presupuestoMax = presupuestoMax - (float(reserva["vuelo_ida"].precio))   #TODO: NO SE SI EL PASAJERO TOTAL ES NECESARIO, NO SE SI EL PRECIO SERA POR PERSONA O EN TOTAL

    if buscar_vuelta == True and len(vuelos_vuelta) >= numero_vuelo:
        reserva["vuelo_vuelta"] = vuelos_vuelta[numero_vuelo - 1]
        presupuestoMax = presupuestoMax - (float(reserva["vuelo_vuelta"].precio))

    if buscar_alojamiento:
        buscar_hoteles()

    if not usuario_activo["correo"]:
        return render_template("login.html")

    if buscar_alojamiento:
        return render_template("hoteles.html", hoteles=lista_hoteles, accion="Cerrar sesión", metodo_accion="cerrar_sesion")

    return(terminar_reserva(hotel="", precio_hotel=0))


@app.route("/reservar/<int:numero_vuelo>", methods=["GET", "POST"])
def buscar_hoteles():
    '''
    Method name: buscar_hoteles
	Description of the Method: Busca hoteles en la página de Amadeus y los almacena en la lista
    '''
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
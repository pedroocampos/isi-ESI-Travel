from amadeus import Client, ResponseError

class Vuelo:
    def __init__(self, id, origen, destino, fecha, horaSalida, horaLlegada, compania, paradas, precio, asientosDisponibles):
        self.id = id
        self.origen = origen
        self.destino = destino
        self.fecha = fecha
        self.horaSalida = horaSalida
        self.horaLlegada = horaLlegada
        self.compania = compania
        self.paradas = paradas
        self.precio = precio
        self.asientosDisponibles = asientosDisponibles

    def __str__(self):
        return "ID: " + str(self.id) + "\nOrigen: " + self.origen + "\nDestino: " + self.destino + "\nFecha: " + self.fecha + "\nHora salida: " + self.horaSalida + "\nHora llegada: " + self.horaLlegada + "\nCompañia: " + self.compania + "\nParadas: " + str(self.paradas) + "\nPrecio: " + str(self.precio) + "\nAsientos disponibles: " + str(self.asientosDisponibles)

class busqueda_vuelos():
    def __init__(self):
        self.lista = []

    def busqueda(self):
        amadeus = Client(
            client_id='H8Ci5KBBxNg7dGQ5gScDxk6feM8IGYwd',
            client_secret='Oe9kxiuyw6ORXZVW'
        )

        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode='MAD',
                destinationLocationCode='BCN',
                departureDate='2023-04-11',
                adults='2',
                children='1',
                infants='1',
                nonStop='true'
            )
            return response.data

        except ResponseError as error:
            print(error)
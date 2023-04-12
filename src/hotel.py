from amadeus import Client, ResponseError

class Hotel():
    def __init__(self, id, nombre,precio, fechaSalida, fechaEntrada):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.fechaSalida = fechaSalida
        self.fechaEntrada = fechaEntrada

    def __str__(self):
        return "ID: " + self.id + "\nNombre: " + self.nombre + "\nUbicacion: " + "\nEstrellas: " + str(self.estrellas) + "\nPrecio: " + str(self.precio) + "\nFecha de salida: " + self.fechaSalida + "\nFecha de entrada: " + self.fechaEntrada

class busqueda_hoteles():
    def __init__(self):
        self.lista = []

    def busqueda(self):
        amadeus = Client(
            client_id='H8Ci5KBBxNg7dGQ5gScDxk6feM8IGYwd',
            client_secret='Oe9kxiuyw6ORXZVW'
        )

        try:
            response = amadeus.reference_data.locations.hotels.by_city.get(
                cityCode = 'LHR',
            )

            for i in range(0, len(response.data) - 1):
                self.lista.append(response.data[i]['hotelId'])


            response_ofertas = amadeus.shopping.hotel_offers_search.get(
                hotelIds = self.lista,
                checkInDate = '2023-04-22',
                checkOutDate = '2023-04-23',
                adults = 2
            )

            print(response_ofertas.data)

            return response_ofertas.data

        except ResponseError as error:
            print(error)
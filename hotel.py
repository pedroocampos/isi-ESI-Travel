from amadeus import Client, ResponseError

class Hotel():
    def __init__(self, id, nombre, ubicacion, estrellas, precio, fechaSalida, fechaEntrada, disponibilidad):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.estrellas = estrellas
        self.precio = precio
        self.fechaSalida = fechaSalida
        self.fechaEntrada = fechaEntrada
        self.disponibilidad = disponibilidad
    
    def __str__(self):
        return "ID: " + self.id + "\nNombre: " + self.nombre + "\nUbicacion: " + self.ubicacion + "\nEstrellas: " + str(self.estrellas) + "\nPrecio: " + str(self.precio) + "\nFecha de salida: " + self.fechaSalida + "\nFecha de entrada: " + self.fechaEntrada + "\nDisponibilidad: " + str(self.disponibilidad)

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
                cityCode = 'BCN',
                radius = 10
            )

            for i in range(0, len(response.data)):
                self.lista.append(response.data[i]['hotelId'])

            response = amadeus.shopping.hotel_offers_search.get(
                hotelIds = self.lista,
                adults = 3
            )
            
            return response.data 
                
        except ResponseError as error:
            print(error)
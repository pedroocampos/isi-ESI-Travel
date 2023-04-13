from amadeus import Client, ResponseError

'''
    Class Name: vuelo.py
    Author/s name: Raul Calzado Olmo, Pedro Campos Castellanos, Raúl González Velázquez
    Release/Creation date: 13/04/2023
    Class description: Clase que representa un vuelo.
'''

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
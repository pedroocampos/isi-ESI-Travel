from amadeus import Client, ResponseError

'''
    Class Name: hotel.py
    Author/s name: Raul Calzado Olmo, Pedro Campos Castellanos, Raúl González Velázquez
    Release/Creation date: 13/04/2023
    Class description: Clase que representa un hotel.
'''

class Hotel():
    def __init__(self, id, nombre,precio, fechaSalida, fechaEntrada):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.fechaSalida = fechaSalida
        self.fechaEntrada = fechaEntrada

    def __str__(self):
        return "ID: " + self.id + "\nNombre: " + self.nombre + "\nPrecio: " + str(self.precio) + "\nFecha de salida: " + self.fechaSalida + "\nFecha de entrada: " + self.fechaEntrada
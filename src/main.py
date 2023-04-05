from hotel import Hotel, busqueda_hoteles
from vuelo import Vuelo, busqueda_vuelos

def main():
    bh = busqueda_hoteles()
    lista = bh.busqueda()
    hotel = Hotel(
        id = lista[0]['hotel']['hotelId'],
        nombre = lista[0]['hotel']['name'],
        ubicacion = str(lista[0]['hotel']['latitude']) + ", " + str(lista[0]['hotel']['longitude']),
        estrellas = 2,
        #estrellas = No hay estrellas en la API
        precio = lista[0]['offers'][0]['price']['total'],
        fechaSalida = lista[0]['offers'][0]['checkOutDate'],
        fechaEntrada = lista[0]['offers'][0]['checkInDate'],
        disponibilidad = lista[0]['available']
    )
    print(hotel)
    
    print("\n--------------------------------\n")
    
    bv = busqueda_vuelos()
    listaVuelos = bv.busqueda()
    vuelo = Vuelo(
        id = listaVuelos[0]['id'],
        origen = listaVuelos[0]['itineraries'][0]['segments'][0]['departure']['iataCode'],
        destino = listaVuelos[0]['itineraries'][0]['segments'][0]['arrival']['iataCode'],
        fecha = listaVuelos[0]['itineraries'][0]['segments'][0]['departure']['at'][0:10],
        horaSalida = listaVuelos[0]['itineraries'][0]['segments'][0]['departure']['at'][11:16],
        horaLlegada = listaVuelos[0]['itineraries'][0]['segments'][0]['arrival']['at'][11:16],
        compania = listaVuelos[0]['itineraries'][0]['segments'][0]['carrierCode'],
        paradas = listaVuelos[0]['itineraries'][0]['segments'][0]['numberOfStops'],
        precio = listaVuelos[0]['price']['total'],
        asientosDisponibles = listaVuelos[0]['numberOfBookableSeats'] 
    )
    print(vuelo)

if __name__ == '__main__':
    main()
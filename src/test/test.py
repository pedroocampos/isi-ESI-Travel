from amadeus import Client, ResponseError

amadeus = Client(
            client_id='H8Ci5KBBxNg7dGQ5gScDxk6feM8IGYwd',
            client_secret='Oe9kxiuyw6ORXZVW'
        )

def buscar_hotel_extranjero():
    '''
    Comprueba si se encuentran ofertas de hoteles extranjeros.
    En este caso hemos elegido París
    '''
    lista = []
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
                cityCode = 'CDG',
                )
        print("Test de búsqueda de hoteles en París .... OK")

    except ResponseError:
        print("Test de búsqueda de ofertas de hotel en París .... FALLO")

    for i in range(0, len(response.data) - 1):
        lista.append(response.data[i]['hotelId'])

    try:
        amadeus.shopping.hotel_offers_search.get(
            hotelIds = lista,
            checkInDate = '2023-04-22',
            checkOutDate = '2023-04-23',
            adults = 2
        )
        print("Test de búsqueda de ofertas de hotel en París .... OK")

    except ResponseError:
        print("Test de búsqueda de ofertas de hotel en París .... FALLO")

def buscar_hotel_nacional():
    '''
    Comprueba si se encuentran ofertas de hoteles nacionales.
    En este caso hemos elegido Barcelona
    '''
    lista = []
    try:
        response = amadeus.reference_data.locations.hotels.by_city.get(
                cityCode = 'BCN',
                )
        print("Test de búsqueda de hoteles en Barcelona .... OK")

    except ResponseError:
        print("Test de búsqueda de hoteles en Barcelona .... FALLO")


    for i in range(0, len(response.data) - 1):
        lista.append(response.data[i]['hotelId'])

    try:
        amadeus.shopping.hotel_offers_search.get(
            hotelIds = lista,
            checkInDate = '2023-04-22',
            checkOutDate = '2023-04-23',
            adults = 2
        )
        print("Test de búsqueda de ofertas de hotel en Barcelona .... OK")

    except ResponseError:
        print("Test de búsqueda de ofertas de hotel en Barcelona .... FALLO")

def buscar_vuelo_extranjero():
    '''
    Comprueba si se encuentran ofertas de vuelos con destino extranjero.
    En este caso hemos elegido un vuelo Madrid -> Londres
    '''

    try:
        amadeus.shopping.flight_offers_search.get(
            originLocationCode='MAD',
            destinationLocationCode='LHR',
            departureDate='2023-04-22',
            adults='2',
            children='1',
            infants='1',
            nonStop='true'
        )
        print("Test de búsqueda de ofertas de vuelo Madrid -> Londres .... OK")

    except ResponseError:
        print("Test de búsqueda de ofertas de vuelo Madrid -> Londres .... FALLO")

def buscar_vuelo_nacional():
    '''
    Comprueba si se encuentran ofertas de vuelos nacionales.
    En este caso hemos elegido un vuelo Madrid -> Barcelona
    '''

    try:
        amadeus.shopping.flight_offers_search.get(
            originLocationCode='MAD',
            destinationLocationCode='BCN',
            departureDate='2023-04-22',
            adults='2',
            children='1',
            infants='1',
            nonStop='true'
        )
        print("Test de búsqueda de ofertas de vuelo Madrid -> Barcelona .... OK")

    except ResponseError:
        print("Test de búsqueda de ofertas de vuelo Madrid -> Barcelona .... FALLO")


buscar_hotel_extranjero()
buscar_hotel_nacional()
buscar_vuelo_extranjero()
buscar_vuelo_nacional()
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='API_KEY',
    client_secret='API_SECRET'
)

try:
    response = amadeus.reference_data.flights.get(
        originLocationCode = 'MAD',
        destinationLocationCode = 'BCN',
        departureDate = '2021-01-01',
        adults = 1
    )

    id = response.data[0]['hotelId']
    directo = response.data[0]['nonStop']
    precioMax = response.data[0]['maxPrice']

    print("ID: " + id + "\nDirecto: " + directo + "\nPrecioMaximo: " + precioMax)

    lista = [id]
    response = amadeus.air.shopping.flight_offers_search.get(
        originLocationCode = 'MAD',
        destinationLocationCode = 'BCN',
        departureDate = '2021-01-01',
        adults = 1
    )

    print(response)

except ResponseError as error:
    print(error)

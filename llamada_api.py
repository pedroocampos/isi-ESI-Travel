from amadeus import Client, ResponseError

amadeus = Client(
    client_id='API_KEY',
    client_secret='API_SECRET'
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='MAD',
        destinationLocationCode='BCN',
        departureDate='2023-03-13',
        adults='2',
        children='1',
        infants='1',
        nonStop='true'
    )
    print(response.data[0]['price']['grandTotal'])
except ResponseError as error:
    print(error)

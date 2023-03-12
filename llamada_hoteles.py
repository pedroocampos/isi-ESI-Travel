from amadeus import Client, ResponseError

amadeus = Client(
    client_id='API_KEY',
    client_secret='API_SECRET'
)

try:
    response = amadeus.reference_data.locations.hotels.by_city.get(
        cityCode = 'BCN',
        radius = 10
    )
    id = response.data[0]['hotelId']
    nombre = response.data[0]['name']
    ciudad = response.data[0]['iataCode']
    direccion = response.data[0]['address']['countryCode']
    
    print("ID: " + id +"\nNombre: " + nombre +"\nCiudad: " + ciudad + "\nDireccion: " + direccion)
    
    lista = [id]
    response = amadeus.shopping.hotel_offers_search.get(
        hotelIds = lista,
        adults = 3
    )
    print(response) #Imprime: <amadeus.client.response.Response object at 0x7f5ef6bea100>
        
except ResponseError as error:
    print(error)

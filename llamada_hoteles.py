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
except ResponseError as error:
    print(error)

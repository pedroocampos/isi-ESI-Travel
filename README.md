# isi-ESI-Travel

## Enlace a las APIs:
  * Ofertas de vuelos: https://developers.amadeus.com/self-service/category/air/api-doc/flight-offers-search
  * Lista de hoteles: https://developers.amadeus.com/self-service/category/hotel/api-doc/hotel-list
  * Ofertas de hoteles: https://developers.amadeus.com/self-service/category/hotel/api-doc/hotel-search
  
## Funcionamiento
Se necesita una versión de Python mayor o igual a la 3.8
Lo primero que se debe hacer es crear un entorno virtual e instalar las dependencias usando el requeriments.txt con el comando:

    pip install -r requirements.txt
    
Y para empezar a hacer llamadas hay que [registrarse](https://developers.amadeus.com/register) y [crear un proyecto](https://developers.amadeus.com/my-apps). Después de hacer esto, se verá la sección de 'API Keys' y esas son las claves que hay que poner en el código. Ejemplo de llamada:

    from amadeus import Client, ResponseError

    amadeus = Client(
        client_id='API_KEY', # que cada uno ponga la suya
        client_secret='API_SECRET'
    )

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='MAD',
            destinationLocationCode='ATH',
            departureDate='2022-11-01',
            adults=1)
        print(response.data)
    except ResponseError as error:
        print(error)
        
Repositorio de apoyo: https://github.com/amadeus4dev/amadeus-python

# isi-ESI-Travel

## Enlace a las APIs:
  * Ofertas de vuelos: https://developers.amadeus.com/self-service/category/air/api-doc/flight-offers-search
  * Lista de hoteles: https://developers.amadeus.com/self-service/category/hotel/api-doc/hotel-list
  * Ofertas de hoteles: https://developers.amadeus.com/self-service/category/hotel/api-doc/hotel-search
  
## Funcionamiento
Se necesita una versión de Python mayor o igual a la 3.8

Lo primero que se debe hacer es activar el entorno virtual con el comando:

    source bin/activate
    
Posteriormente, para construir y poder utilizar la imagen Docker se deben utilizar estos comandos:

    sudo docker build -f Dockerfile -t esi-travel:latest .
   
    sudo docker run -p 2001:5000 -i esi-travel
 
En el código ya hay unas claves puestas para poder hacer llamadas a las APIs, pero si quieres generar las tuyas hay que seguir estos pasos:
    
Primero hay que [registrarse](https://developers.amadeus.com/register) y [crear un proyecto](https://developers.amadeus.com/my-apps). Después de hacer esto, se verá la sección de 'API Keys' y esas son las claves que hay que poner en el código.
        
Repositorio de apoyo: https://github.com/amadeus4dev/amadeus-python

## Autores del proyecto
Pedro Campos Castellanos, Raúl Calzado Olmo y Raúl González Velázquez

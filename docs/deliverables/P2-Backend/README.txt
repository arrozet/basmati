- Todos los archivos de los microservicios REST y los scripts de Docker (incluyendo el docker compose) están en la carpeta "backend". Hay un dockerfile dentro de la carpeta de cada microservicio

- Se adjunta un .env con las variables de entorno de la URI de la base de datos de MongoDB Atlas y una API key necesaria para el servicio de integración. La URI de la base de datos también está en el apartado "3.3. Despliegue en Atlas y URI" de la memoria técnica.

- La localización de la especificación OpenAPI es la común usada en FastAPI. Cabe destacar que en el API Gateway están todas las especificaciones OpenAPI agregadas, provenientes de todos los microservicios:

1. API Gateway: localhost:8000/docs
2. User Service: localhost:8001/docs
3. Calendar Service: localhost:8002/docs
4. Event Service: localhost:8003/docs
5. Notification Service: localhost:8004/docs
6. Integration Service: localhost:8006/docs

- Para probar los endpoints se recomienda primero crear el tipo de entidad a probar con el POST del CRUD y coger su ID o atributo necesario para probar el resto de elementos. Esto no es necesario hacerlo con los POST y PUT, ya que tienen su request body predefinido como ejemplo. No podemos indicar explícitamente la ID porque esta la crea MongoDB cada vez que se crea un usuario, por lo que podría llegar a ser problemático hardcodear una ID en las pruebas (depende del orden en el que se ejecute, por ejemplo, primero el DELETE, el GET fallaría).

- Igualmente, toda esta información también está disponible en la URL del repositorio alojado en GitHub: https://github.com/arrozet/basmati


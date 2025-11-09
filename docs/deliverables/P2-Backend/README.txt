- Todos los archivos de los microservicios REST y los scripts de Docker (incluyendo el docker compose) están en la carpeta "backend". Hay un dockerfile dentro de la carpeta de cada microservicio

- Se adjunta un .env con las variables de entorno de la URI de la base de datos de MongoDB Atlas y una API key necesaria para el servicio de integración. La URI de la base de datos también está en el apartado "3.3. Despliegue en Atlas y URI" de la memoria técnica.

- La localización de la especificación OpenAPI es la común usada en FastAPI. Cabe destacar que en el API Gateway están todas las especificaciones OpenAPI agregadas, provenientes de todos los microservicios:

1. API Gateway: localhost:8000/docs
2. User Service: localhost:8001/docs
3. Calendar Service: localhost:8002/docs
4. Event Service: localhost:8003/docs
5. Notification Service: localhost:8004/docs
6. Integration Service: localhost:8006/docs

- Igualmente, toda esta información también está disponible en la URL del repositorio alojado en GitHub: https://github.com/arrozet/basmati


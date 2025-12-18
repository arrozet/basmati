# UNIVERSIDAD DE MÁLAGA

**Departamento de Lenguajes y Ciencias de la Computación**
**Ingeniería Web 2025/26**

# Práctica de servicios Web (II): frontend

[cite_start]En esta práctica desarrollaréis un frontend para los servicios REST implementados en la práctica anterior[cite: 8]. [cite_start]En particular, implementaréis el frontend utilizando las tecnologías que elijáis (Java, Python, HTML+JS, AngularJS, React, Next.js, etc.)[cite: 9].

[cite_start]Se valorará tanto la funcionalidad como el diseño de la aplicación: estilos y tipos de letra, colores, imágenes, layout, diseño adaptativo (responsive), etc[cite: 10].

[cite_start]El frontend hará uso de los microservicios de las entidades desplegados en la práctica anterior, con objeto de dotar a la aplicación web del caso de estudio de una capa de presentación[cite: 11]. [cite_start]Dicha capa de presentación puede ser generada por el backend, o por una aplicación GUI independiente del mismo[cite: 12]. [cite_start]En caso de existir de forma independiente, el frontend puede consistir en una aplicación de escritorio a ejecutar en el ordenador del usuario, o alojarse en algún proveedor cloud como Netlify u otros[cite: 13].

### Funcionalidad

[cite_start]El frontend posibilitará al usuario realizar la siguiente funcionalidad[cite: 14]:

- [cite_start]El frontend permitirá la creación, edición y mantenimiento de calendarios, eventos y sus contenidos asociados[cite: 15].
- [cite_start]Mediante el navegador, los usuarios podrán crear calendarios sobre un determinado tema y añadir, modificar, corregir o eliminar eventos a los mismos[cite: 16].
- [cite_start]Todos estos contenidos serán compartidos con cualquier otro usuario[cite: 17].
- [cite_start]Cada evento consistirá en contenido textual acompañado de imágenes, archivos adjuntos, mapas, etc[cite: 18].
- [cite_start]Los usuarios podrán buscar calendarios y eventos a partir de diversos criterios (por separado o combinados), tales como palabras clave, fecha de creación (rango), organizador (quién ha creado el calendario), etc[cite: 19].

### Modificaciones en Backend/API

[cite_start]Si para realizar esta práctica es necesario modificar el diseño de la base de datos o de la API REST, os aseguraréis de que la entrega anterior siga funcionando, utilizando para ello mecanismos de versionado de la API o los datos, controlando los problemas o errores que tenga la coexistencia de distintas versiones del modelo de datos en la misma BD[cite: 20].

[cite_start]En caso de que necesitéis modificar la API REST respecto a la entrega anterior, modificad también e incluid en la entrega su especificación OpenAPI o el conjunto de pruebas Postman necesario para utilizarla[cite: 21].

### Integraciones Específicas

[cite_start]Además, integraréis en vuestra aplicación funcionalidad relativa a algunos de los requisitos mencionados en el caso de estudio, en particular mapas, imágenes, comentarios y notificaciones[cite: 22]:

- [cite_start]**Visualización de mapas.** La aplicación permitirá la visualización de mapas, ya sean OpenStreetMap, Google Maps u otro sistema similar, que mostrarán la localización de información relevante para el caso de estudio (por ejemplo, la localización de los eventos a los que se refiere un calendario)[cite: 24]. [cite_start]Si es preciso realizar funciones de geocoding se utilizará algún mecanismo de caching que evite la reiteración de llamadas que acaben agotando las cuotas de los servicios[cite: 25].

- [cite_start]**Visualización de imágenes.** La aplicación permitirá la visualización de imágenes y/o gráficos, de acuerdo con los requisitos del caso de estudio (por ejemplo, relativas a los eventos)[cite: 26]. [cite_start]Las imágenes se cargarán en la aplicación desde un archivo (no a partir de una URL) y deberán ser almacenadas en algún servicio cloud, bien en el propio servidor o bien externo, como por ejemplo Cloudinary o Dropbox[cite: 27].

- [cite_start]**Comentarios y notificaciones.** La aplicación permitirá realizar comentarios sobre los calendarios o eventos organizados por otros usuarios[cite: 28]. [cite_start]Los organizadores recibirán una notificación cuando otro usuario haya comentado alguno de sus eventos, pudiendo cada usuario configurar si dichas notificaciones se reciben por e-mail o la siguiente vez que se conecte a la aplicación[cite: 29].

[cite_start]De nuevo, no incluiremos en esta entrega la identificación de usuarios, que abordaremos en la última entrega[cite: 30].

---

## Modo de entrega

[cite_start]Esta práctica se entregará en grupo a través del campus virtual, mediante un archivo comprimido que contendrá[cite: 38]:

1.  [cite_start]**Una memoria técnica**, que será importante en la evaluación de la práctica ya que en ella se describirán las decisiones de diseño e implementación, en particular[cite: 39]:

    - [cite_start]Cualquier replanteamiento de decisiones anteriores (de tecnologías a utilizar u otros) o cambios en el diseño de la base de datos o la implementación de los servidores web[cite: 40].
    - [cite_start]Los principales requisitos considerados en la práctica[cite: 41].
    - [cite_start]Las tecnologías utilizadas en la práctica (lenguajes, bibliotecas, frameworks, base de datos, etc.) y la URL de la base de datos (sea local o en la nube) o las instrucciones para acceder a ella[cite: 42].
    - [cite_start]Instrucciones de instalación/despliegue de la aplicación, en particular las instrucciones de despliegue en Docker y para crear y poblar la base de datos si esto es conveniente para el funcionamiento de los servicios y las pruebas[cite: 43].
    - [cite_start]La funcionalidad del frontend, detallando la integración que hace de servicios externos (mapas, imágenes, etc.)[cite: 44].

2.  [cite_start]**Las fuentes del frontend desarrollado**, así como de los microservicios REST y esquemas de definición de la base datos realizados para la práctica anterior si ha sido necesario modificarlos para completar esta entrega[cite: 45].

3.  [cite_start]**Scripts Docker** para desplegar tanto el frontend como los microservicios que utiliza en el backend y la base de datos (si es local)[cite: 46].

4.  [cite_start]**Cualquier archivo de configuración** que defina variables de entorno necesarias para desplegar el sistema[cite: 47].

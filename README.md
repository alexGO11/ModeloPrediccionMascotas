# Mapa web para visualizar datos de contagio de mascotas

## Descripción
Este proyecto de final de carrera es una aplicación que permite visualizar en un mapa de España la incidencia de determinadas enfermedades de mascotas. Se ejecuta con un frontend en React y un backend basado en FastAPI (Python) ejecutandose en contenedores mediante Docker Compose.

## Tecnologías utilizadas
- **Frontend**: React
- **Backend**: FastAPI (Python)
- **Base de datos**: MySQL
- **Orquestación**: Docker Compose

## Prerrequisitos
Antes de comenzar, asegúrate de tener instalado en tu sistema Docker:
- [Docker](https://www.docker.com/get-started)

## Instalación y ejecución
1. Clona este repositorio:
   ```sh
   git clone https://github.com/usuario/ModeloPrediccionMascotas.git
   cd ModeloPrediccionMascotas

2. Crea un archivo [.env] en la raíz del proyecto y configura las variables de entorno necesarias.

3. Construye y levanta los contenedores con Docker Compose:
    ```sh
    docker compose up --build

4. Para subir los archivos entre en el siguiente enlace:
    - http://localhost:8000/docs
    - Una vez dentro inserte los archivos correspondientes en los endpoints de upload_csv y add_human_data

5. La aplicación estará disponible en:
    - https://localhost


## Variables de entorno
- MYSQL_ROOT_PASSWORD : La contraseña del usuario root de MySQL
- MYSQL_DATABASE : La base de datos por defecto a crear
- DB_HOST : El host del servidor de la base de datos
- DB_USER : El usuario de la base de datos
- DB_PASSWORD : La contraseña del usuario de la base de datos
- DB_NAME : El nombre de la base de datos a la que conectarse
- DB_DIALECT : El dialecto/driver de SQLAlchemy a usar para la conexión (por ejemplo, mysql+pymysql)

El archivo __.env.example__ se puede usar como modelo, copielo y complete los campos faltantes. 
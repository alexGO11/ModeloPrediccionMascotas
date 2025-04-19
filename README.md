# Mapa web para visualizar datos de contagio de mascotas

## Descripción
Este proyecto es una aplicación que permite visualizar en un mapa de la península la incidencia de determinadas enfermedades de mascotas. Se ejecuta con un frontend en React y un backend basado en FastAPI (Python). Ambos servicios se ejecutan en contenedores mediante Docker Compose.

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

2. Crea un archivo [.env] en la raíz del proyecto y configura las variables de entorno necesarias (puedes usar .env.example como referencia).

3. Construye y levanta los contenedores con Docker Compose:
    ```sh
    docker compose up --build

4. La aplicación estará disponible en:
    - http://localhost

## Estructura del proyecto
```sh
ModeloPrediccionMascotas/
│── backend/           # Código del backend
│   ├── src/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│── frontend/          # Código del frontend
│   ├── app/
│   ├── package.json
│   ├── Dockerfile
│── docker-compose.yml 
│── .env.example       


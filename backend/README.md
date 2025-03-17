# ModeloPrediccionMascotas

#activar entorno virtual: 1. Set-ExecutionPolicy Unrestricted -Scope CurrentUser 2. .\backend\.venv\Scripts\activate

#abrir base de datos en docker
docker exec -it db mysql -u root -p

#crear network en docker 1. docker network <name> 2. docker network connect <net name> <container name>

#crear contenedor para backend en docker
docker run --name backend -p 8000:8000 -w /app -v C:\Users\pablo\Desktop\tfg\ModeloPrediccionMascotas\backend:/app -d python
(nombre) (puerto) (directorio donde (directorio local enlazado con el contenedor) (dialecto)
guardar el contenedor)

    docker run --name backend -p 8000:8000 -w /app -v C:\Users\pablo\Desktop\tfg\ModeloPrediccionMascotas\backend:/app -d -it python bash

#ejecutar contenedor del backend
uvicorn main:app --reload --host 0.0.0.0

#inicializar front end (desde carpeta frontend)
npm start

#inicializar backend
docker exec -it backend /bin/bash

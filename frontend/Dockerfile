# Frontend part
FROM node:23-alpine

WORKDIR /app

COPY package*.json ./

# Instala dependencias y react-router-dom directamente
RUN npm install && npm install react-router-dom && npm install axios && npm install bootstrap

COPY . .

RUN npm run build
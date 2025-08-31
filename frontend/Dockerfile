# Etapa 1: Frontend part
FROM node:23-alpine as build

WORKDIR /app

COPY package*.json ./

# Instala dependencias y react-router-dom directamente
RUN npm install && npm install react-router-dom && npm install axios && npm install bootstrap

COPY . .

RUN npm run build

# Etapa 2: Nginx para servir la app
FROM nginx:stable-alpine

# Copia el build generado al directorio de Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copia la configuración de Nginx
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copia los certificados SSL
COPY certbot/conf/selfsigned.crt /etc/ssl/certs/selfsigned.crt
COPY certbot/conf/selfsigned.key /etc/ssl/private/selfsigned.key


# Exponer el puerto 443
EXPOSE 443

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
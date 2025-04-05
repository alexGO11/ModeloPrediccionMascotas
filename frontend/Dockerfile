# Frontend part
FROM node:23-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY . .

RUN npm run build

#Nginx part
FROM nginx:stable-alpine

COPY --from=build /app/build /bin/www

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

ENV PORT=80

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]
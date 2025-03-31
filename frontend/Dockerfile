FROM node:23-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ENV PORT=8080

RUN npm run build

EXPOSE 8080

CMD ["npm", "start"]
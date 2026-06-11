FROM node:20-alpine
RUN apk add --no-cache git
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 7860
ENV PORT=7860
CMD ["node", "server.js"]

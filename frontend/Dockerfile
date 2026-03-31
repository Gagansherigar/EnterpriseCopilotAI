FROM node:22 AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend .
RUN npm run build


FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# ✅ FIXED (proper escaping)
RUN printf "server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / {\n\
    try_files \$uri \$uri/ /index.html;\n\
  }\n\
  location /assets/ {\n\
    try_files \$uri =404;\n\
  }\n\
}\n" > /etc/nginx/conf.d/default.conf
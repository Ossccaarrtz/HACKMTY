# Imagen base de Nginx
FROM nginx:alpine

# Elimina archivos por defecto de Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia todos los archivos del frontend actual
# (index.html, script.js, style.css, etc.)
COPY ./app/frontend/ /usr/share/nginx/html/

# Expone el puerto del contenedor web
EXPOSE 80

# Inicia Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]

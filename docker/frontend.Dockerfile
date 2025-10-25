FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY app/frontend/ .
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

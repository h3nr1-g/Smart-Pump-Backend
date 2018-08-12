FROM debian:stretch-slim

RUN apt-get update -y
RUN apt-get install -y nginx net-tools

RUN mkdir -p /var/www/static

COPY sites-enabled/default /etc/nginx/sites-enabled/default

CMD ["nginx", "-g", "daemon off;"]

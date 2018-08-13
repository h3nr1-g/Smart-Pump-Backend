# Docker Compose Example

## Description
This folder contains a Docker (Compose) based deployment example.

The example consists of two docker containers:
  * **nginx**: Inside this container a nginx web server runs and is used as the central gateway of the system

  * **gunicorn**: This container is used as an application server. For the provision of the application logic the WSGI HTTP server gunicorn (http://gunicorn.org/) is used.

## Run Example

Open a shell:
```
cd Smart-Pump-Backend/docker
docker-compose up
```

Open the link http://localhost/monitor/login


## Dummy Credentials
```
User: admin
Password: admin123456789
```

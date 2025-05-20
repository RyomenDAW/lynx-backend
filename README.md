LYNX - Dockerización y Despliegue en AWS
Descripción
Este proyecto involucra la implementación y despliegue de una plataforma de gestión de videojuegos llamada LYNX, desarrollada con Angular (frontend) y Django (backend). El proyecto ha sido dockerizado para facilitar su despliegue y ejecución en contenedores, y se ha configurado para ser desplegado en una instancia de AWS.

Requisitos Previos
Antes de comenzar, asegúrate de tener los siguientes programas y herramientas instaladas:

1. Instalar Docker y Docker Compose en Ubuntu
Si no tienes Docker instalado en tu sistema, sigue estos pasos para instalarlo:

Actualizar el sistema:

bash
Copy
sudo apt-get update
Instalar Docker:

bash
Copy
sudo apt-get install docker.io -y
Iniciar y habilitar Docker para que se inicie al arranque:

bash
Copy
sudo systemctl enable --now docker
Verificar que Docker esté correctamente instalado:

bash
Copy
sudo docker --version
2. Instalar Docker Compose
Instalar Docker Compose:

bash
Copy
sudo apt-get install -y python3-pip
sudo pip3 install docker-compose
Verificar la instalación de Docker Compose:

bash
Copy
docker-compose --version
3. Instalar Python y Pip
Si no tienes Python instalado, sigue estos pasos:

Instalar Python 3.10:

bash
Copy
sudo apt-get install python3.10 -y
Instalar pip para Python 3:

bash
Copy
sudo apt-get install python3-pip -y
Verificar que Python y pip estén correctamente instalados:

bash
Copy
python3 --version
pip3 --version
4. Clonar los Repositorios
Clonar el repositorio del backend:

bash
Copy
git clone https://github.com/RyomenDAW/lynx-backend.git
cd lynx-backend
Clonar el repositorio del frontend:

bash
Copy
git clone https://github.com/RyomenDAW/lynx-frontend.git
cd lynx-frontend
Configuración de Docker
1. Crear el archivo Docker Compose
Asegúrate de que el archivo docker-compose.yml esté en la carpeta raíz del proyecto (por ejemplo, en ~/Desktop/lynx/).

Contenido de docker-compose.yml:
yaml
Copy
version: '3.8'

services:
  backend:
    build:
      context: ./lynx-backend
    container_name: lynx-backend
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=mysite.settings
    volumes:
      - ./lynx-backend:/app
    restart: unless-stopped

  frontend:
    build:
      context: ./lynx-frontend
    container_name: lynx-frontend
    ports:
      - "80:80"
    restart: unless-stopped
Este archivo define los servicios para el frontend y el backend.

2. Dockerfiles
Dockerfile para el frontend:
dockerfile
Copy
# Dockerfile para frontend Angular

# Etapa de construcción
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --prod

# Etapa para servir con nginx
FROM nginx:alpine
COPY --from=build /app/dist/lynx-app /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
Dockerfile para el backend:
dockerfile
Copy
# Dockerfile para backend Django

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

# Exponer puerto 8000
EXPOSE 8000

# Ejecutar Gunicorn para producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysite.wsgi:application"]
Construcción y Ejecución de los Contenedores
Una vez que hayas configurado los Dockerfiles y el archivo docker-compose.yml, procede a construir y ejecutar los contenedores de la siguiente manera:

1. Construir los contenedores
Construir los contenedores sin caché:

bash
Copy
sudo docker-compose build --no-cache
Levantar los contenedores:

bash
Copy
sudo docker-compose up
2. Verificar que todo está funcionando
Una vez que los contenedores estén en ejecución, podrás acceder al frontend a través de la IP pública de tu instancia de AWS en el puerto 80, y al backend en el puerto 8000.

Despliegue en AWS
Para desplegar la aplicación en AWS EC2, sigue estos pasos:

1. Crear las instancias EC2
Crea dos instancias EC2 (una para el frontend y otra para el backend).

Asegúrate de que ambas instancias estén en la misma VPC y tengan configurados los grupos de seguridad para permitir la comunicación entre ellas.

Asigna Elastic IPs a las instancias para que puedan ser accesibles desde internet.

2. Subir los archivos a las instancias EC2
Usa scp o cualquier otra herramienta para subir los archivos de frontend y backend a las instancias correspondientes.

3. Instalar Docker y Docker Compose en las instancias EC2
Instalar Docker en la instancia EC2:

bash
Copy
sudo apt-get update
sudo apt-get install docker.io -y
sudo systemctl enable --now docker
Instalar Docker Compose:

bash
Copy
sudo apt-get install -y python3-pip
sudo pip3 install docker-compose
4. Subir el código al servidor
Sube las carpetas lynx-backend y lynx-frontend a las instancias EC2.

5. Ejecutar Docker Compose en las instancias EC2
En cada instancia EC2, navega a la carpeta donde subiste los archivos y ejecuta:

bash
Copy
sudo docker-compose up --build
Esto construirá y levantará ambos contenedores (frontend y backend) en sus respectivas instancias.

Notas Adicionales
Problema de CORS: Si estás teniendo problemas con CORS, asegúrate de tener configurado correctamente el middleware de CORS en settings.py de Django. Si estás trabajando en un entorno local o en diferentes instancias, añade las direcciones IP correspondientes a CORS_ALLOWED_ORIGINS en tu configuración.

Probar la API: Accede a la API en el puerto 8000 de la instancia backend para probar las funcionalidades.
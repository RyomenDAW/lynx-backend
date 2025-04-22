# 🕹️ LYNX - Plataforma de Compra y Gestión de Videojuegos

**Repositorio:** [https://github.com/RyomenDAW/lynx-backend](https://github.com/RyomenDAW/lynx-backend)

**Versión actual:** v0.95  
**Backend:** Django 5.1 + Python 3.10  
**Frontend:** Bootstrap 5 + Orbitron / Rajdhani

---

## 📦 Tecnologías

- **Python 3.10** / **Django 5.1**
- **SQLite3** (modo local) o **MySQL** (para producción)
- **Bootstrap 5** + **Orbitron/Rajdhani**
- **Docker** para contenedores (opcional en local)
- **Deploy previsto en AWS EC2**

---

##  Instalación Manual en Ubuntu

### 1. Clonar el proyecto
```bash
git clone https://github.com/RyomenDAW/lynx-backend.git
cd lynx-backend
```

### 2. Crear entorno virtual
```bash
sudo apt-get install python3-venv  # Si no está instalado
python3 -m venv myvenv
source myvenv/bin/activate
```

### 3. Instalar dependencias
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Migrar la base de datos
```bash
python manage.py migrate
```

### 5. Crear superusuario (opcional, para Django admin)
```bash
python manage.py createsuperuser
```

### 6. Lanzar el servidor local
```bash
python manage.py runserver 0.0.0.0:8080
```

### 7. Acceder a la aplicación
[http://127.0.0.1:8080](http://127.0.0.1:8080)

---

## 🐳 Despliegue en Docker

### Dockerfile (base Ubuntu)
```dockerfile
FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip python3-venv git

WORKDIR /lynx
COPY . /lynx

RUN python3 -m venv myvenv
RUN /lynx/myvenv/bin/pip install --upgrade pip
RUN /lynx/myvenv/bin/pip install -r requirements.txt

EXPOSE 8000

CMD ["/lynx/myvenv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Comandos para ejecución
```bash
docker build -t lynx .
docker run -p 8000:8000 lynx
```

---

## 🔐 Permisos

| Rol             | Puede Ver Juegos | Comprar | Canjear Códigos | Crear Juegos | Crear Códigos | Acceso Admin |
|----------------|------------------|---------|------------------|--------------|---------------|--------------|
| Usuario         | ✅               | ✅      | ✅               | ❌           | ❌            | ❌           |
| Moderador/Admin | ✅               | ✅      | ✅               | ✅           | ✅            | ✅           |

---

## 🎮 Funcionalidades Disponibles

- ✅ Registro y login de usuarios
- ✅ Biblioteca de juegos con favoritos y tiempo jugado
- ✅ Tienda de videojuegos con CRUD y compra
- ✅ Sistema de reseñas con puntuación y comentario
- ✅ Códigos promocionales: entrega de saldo o juegos
- ✅ Roles y permisos definidos
- ✅ Sistema de canjeo de códigos
- ✅ Perfil de usuario con saldo y reputación (esto ultimo hay que trabajarlo en la siguiente version)

---

## 📅 Hitos del Proyecto

- Hito 1: Estructura inicial, modelos, templates.
- Hito 2: Versión funcional v0.25 (estado actual).
- Hito 3: Integraciones externas, mejoras visuales y despliegue completo.

---
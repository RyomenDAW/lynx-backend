FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# COPIA EL .env SI LO TIENES FUERA DEL CONTEXTO DE BUILD
# (O bien lo montas desde docker-compose o al lanzar el contenedor)
# COPY .env .  <-- OPCIONAL

# EXPOSE
EXPOSE 8000

# INICIALIZA STATICFILES (si aplica)
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 mysite.wsgi:application"]

FROM python:3.12.0

WORKDIR /Inframe-Backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . ./
#eV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

#NV ALLOWED_HOSTS=$ALLOWED_HOSTS

#NV DEBUG=$DEBUG

#NV SERVER_URL=$SERVER_URL

#UN python manage.py collectstatic --noinput

#MD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]


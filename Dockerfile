FROM python:3.12.0

WORKDIR /Inframe-Backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . ./
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

ENV ALLOWED_HOSTS=$ALLOWED_HOSTS

ENV DEBUG=$DEBUG

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]


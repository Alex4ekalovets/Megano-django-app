FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.5.1"
RUN poetry config virtualenvs.create false --local

COPY pyproject.toml poetry.lock ./
RUN poetry install

#Установка фронтенда
COPY diploma-frontend ./diploma-frontend
WORKDIR /app/diploma-frontend
RUN rm -rf dist && python setup.py sdist && pip install dist/*

WORKDIR /app

COPY mysite .env.template ./

RUN python manage.py collectstatic

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]
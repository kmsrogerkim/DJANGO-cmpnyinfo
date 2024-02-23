FROM python:3.10-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /usr/src/app/
RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "python", "manage.py", "runserver","0.0.0.0:8000"]
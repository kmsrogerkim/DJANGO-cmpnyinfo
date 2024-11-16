FROM python:3.10-alpine

WORKDIR /

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-k", "gevent", "cmpnyinfo.wsgi:application", "--bind", "0.0.0.0:8000"]
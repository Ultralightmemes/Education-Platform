FROM python:3.10

WORKDIR /usr/src/api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./req.txt /usr/src/req.txt
RUN pip install -r /usr/src/req.txt

COPY . /usr/src/api

EXPOSE 8000

CMD ["python", "manage.py", "migrate"]
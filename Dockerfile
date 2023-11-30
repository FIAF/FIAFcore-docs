
FROM python:3.11-alpine

WORKDIR /docs

COPY . /docs

RUN ls -al

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

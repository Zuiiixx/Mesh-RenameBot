FROM python:3.9.1-buster

WORKDIR /usr/src/app

COPY . .

RUN pip install -U -r requirements.txt

EXPOSE 8080

CMD [ "python", "-m", "MeshRenameBot" ]

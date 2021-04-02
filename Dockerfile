FROM steamcmd/steamcmd:ubuntu

RUN apt-get update
RUN apt-get -y install libarchive-tools python3 python3-pip curl

RUN pip3 install sanic scrapy dateparser rsa

COPY . /src

WORKDIR /src

VOLUME [ "/tmp/bluebellws" ]

EXPOSE 8000

CMD ["python3", "main.py"]
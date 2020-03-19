FROM steamcmd/steamcmd:ubuntu

RUN apt-get update && apt-get -y install libarchive-tools python3 python3-pip

RUN pip3 install sanic scrapy dateparser  

COPY . /src

WORKDIR /src

VOLUME [ "/tmp/bluebellws" ]

EXPOSE 8000

CMD ["python3", "main.py"]
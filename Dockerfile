FROM ubuntu:18.04
RUN apt-get update \
    && apt-get install tesseract-ocr -y \
    python3 \
    #python-setuptools \
    python3-pip \
    && apt-get install -y libsm6 libxext6 libxrender-dev

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 8083

#ENTRYPOINT ["python3"]

CMD bash run.sh


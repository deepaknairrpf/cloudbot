FROM python:3.6.10-slim
RUN apt-get clean && apt-get update && apt-get install build-essential -y && apt-get install -y apt-transport-https

RUN apt-get install -y default-libmysqlclient-dev \
    && apt-get clean

RUN apt-get install -y procps && apt-get install -y vim
RUN apt-get install -y curl htop wget
RUN apt-get -y install mariadb-client


COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

ENV PYTHONPATH /app
RUN echo $PYTHONPATH >/usr/local/lib/python3.6/site-packages/dataweave_path.pth

RUN pip install -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
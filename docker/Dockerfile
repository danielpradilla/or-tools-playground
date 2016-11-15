#based on https://github.com/texastribune/docks/tree/master/gunicorn

FROM ubuntu:16.04
MAINTAINER info@danielpradilla.info

RUN apt-get update && apt-get upgrade -y && apt-get update
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get -y install software-properties-common apt-transport-https
RUN apt-get install -yq supervisor

#create working directories
RUN mkdir -p /app/logs
RUN mkdir /app/run
RUN mkdir /app/www

WORKDIR /app

#install http server
RUN apt-get -yq install nginx

#install python
RUN apt-get -y install python python-pip libpq-dev python-dev python-setuptools

#install whats neccessary for or-tools
RUN pip install --upgrade pip
RUN pip install --upgrade wheel setuptools virtualenv
RUN apt-get -y install flex bison
RUN apt-get -y --fix-missing install autoconf libtool zlib1g-dev texinfo help2man gawk g++ curl texlive cmake subversion

#install gunicorn and falcon for providing API endpoints
RUN pip install gunicorn==19.6
RUN pip install falcon

#install or-tools
#https://github.com/google/or-tools/releases/download/v5.0/or-tools_python_examples_v5.0.3919.tar.gz
ADD or-tools_python_examples_v5.0.3919.tar.gz /app
RUN mv /app/ortools* /app/ortools && cd /app/ortools/ && python setup.py install --user

#copy configuration files
ADD gunicorn_conf.py /app/
ADD gunicorn.supervisor.conf /etc/supervisor/conf.d/
ADD nginx.conf /app/
ADD nginx.supervisor.conf /etc/supervisor/conf.d/


VOLUME ["/app/logs","/app/www"]

EXPOSE 80

ENTRYPOINT ["/usr/bin/supervisord", "-n"]

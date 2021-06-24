FROM ubuntu:18.04

RUN \
  export DEBIAN_FRONTEND="noninteractive" && \
  apt-get update && \
  apt-get -y install \
  apache2 \
  php7.2 \
  libapache2-mod-php7.2

RUN a2enmod php7.2

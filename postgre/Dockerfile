FROM postgres:15

RUN apt-get update && \
    apt-get install -y locales-all && \
    locale-gen tr_TR.UTF-8

ENV LANG=tr_TR.UTF-8
ENV LANGUAGE=tr_TR:tr
ENV LC_ALL=tr_TR.UTF-8

FROM ubuntu:latest AS base

FROM base AS apt-packages
    RUN apt-get update
    RUN apt-get install python3.10 -y
    RUN apt-get install python3-pip -y
    RUN apt-get install exiftool -y
    RUN rm -rf /var/lib/apt/lists/*

FROM apt-packages AS pip-requirements
    RUN pip install --upgrade pip
    RUN pip install texttable

FROM pip-requirements AS setup
    WORKDIR /opt
    COPY ./jpeg-investigator ./jpeg-investigator
    RUN chmod +x ./jpeg-investigator/entrypoint.sh

    RUN mkdir /home/workdir
    WORKDIR /home

FROM setup AS finish
    ENTRYPOINT [ "/opt/jpeg-investigator/entrypoint.sh" ]

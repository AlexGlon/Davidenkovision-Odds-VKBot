FROM python:3.8.6

# ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install libpq-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

ADD . /opt/dv-vkbot

COPY requirements.txt /opt/dv-vkbot/requirements.txt
RUN pip install -r /opt/dv-vkbot/requirements.txt --no-cache-dir

# работает с "./usr/bin/python", но крашится из-за не ASCII-символа
ENTRYPOINT ["./usr/bin/python3", "./opt/dv-vkbot/main.py"]


# ADD easycar /opt/easycar
# COPY entrypoint.sh /opt/easycar/entrypoint.sh
# WORKDIR /opt/easycar


# EXPOSE 8000

# ENTRYPOINT [ "/bin/bash", "/opt/easycar/entrypoint.sh" ]
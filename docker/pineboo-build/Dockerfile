FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git libglib2.0-0 libfontconfig1 libgl1 libglx-mesa0 \
    moreutils make poppler-utils \
    python3-pip python3-setuptools \
    python3-psycopg2 python3-mysqldb python3-pymysql python3-venv python3-cryptography \
    libxkbcommon-x11-0 libopengl0 libdbus-1-3 xcb libxcb-cursor0 libegl1-mesa \
    libxml2-dev libxslt1-dev\
    && \
    rm -rf /var/lib/apt/lists/*

COPY pip-requirements.txt /

RUN pip3 install --upgrade pip==25.0.1 --break-system-packages --ignore-installed

RUN pip3 install -r /pip-requirements.txt --prefer-binary --upgrade --no-cache-dir --break-system-packages --ignore-installed

# Use official Python 3.10 base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for inventory management needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libgeos-dev \
    libproj-dev \
    libgdal-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
RUN tar -xzvf Python-3.10.14.tgz
RUN cd Python-3.10.14
WORKDIR Python-3.10.14
RUN ./configure --enable-optimizations --with-system-ffi
RUN make -j 16
RUN make altinstall

WORKDIR /app

COPY ./requirements.txt .
RUN pip3.10 install numpy
RUN pip3.10 install --no-cache-dir -r requirements.txt
RUN pip3.10 install -e git+git@github.com:yourlabs/django-cities-light.git#egg=cities_light
COPY . .
COPY .env /app/.env

    

EXPOSE 7701
CMD ["sh", "-c", "python3.10 manage.py migrate && python3.10 manage.py runserver 0.0.0.0:7701"]
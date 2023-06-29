FROM python:3.9-slim-buster
LABEL maintainer="Chijia Jason"

ENV PYTHONUNBUFFERED 1
ENV PATH="/scripts:${PATH}"
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/flutterjava-firebase.json"

# RUN pip install --upgrade pip
# RUN apk add --update alpine-sdk
# RUN apk add --update --no-cache postgresql-client jpeg-dev
# RUN apk add --update --no-cache --virtual .tmp-build-deps \
#       gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
# RUN apk add --upgrade --no-cache postgis
# RUN apk add --upgrade --no-cache geos gdal 

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get install -y postgis \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app
COPY ./scripts /scripts
RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
# RUN adduser --disabled-password user
# RUN chown -R user:user /vol/
# RUN chmod -R 755 /vol/web
# USER user
# VOLUME /vol/web

CMD ["entrypoint.sh"]

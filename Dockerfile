# FROM alpine:3.7

# WORKDIR /.

# COPY requirements.txt .

# RUN \
#  apk add --no-cache python3 postgresql-libs && \
#  apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
#  python3 -m pip install -r requirements.txt --no-cache-dir && \
#  apk --purge del .build-deps

# COPY . .

# CMD ["python3", "books-api.py"]

FROM python

WORKDIR /app
COPY . /app
# How you install your python packages may differ
RUN pip install -r requirements.txt

# Ensure the path here is correct
ENV FLASK_APP ./books-api.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000


CMD flask run
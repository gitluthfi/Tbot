FROM python:3.7.17-alpine3.18

WORKDIR /app

COPY . . 

RUN apk add --no-cache \
    build-base \
    openblas-dev \
    # Add other BLAS libraries if needed
    && pip install -r requirements.txt \
    && apk del build-base
CMD ["python", "Tbot.py"]
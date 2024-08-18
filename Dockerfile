# syntax=docker/dockerfile:1
# Based on https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

# We use Debian to speed up the installation of Python dependencies
# WHL format is not supported on Alpine
FROM python:3.10-bookworm AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

RUN python3 /app/listing_gen.py
EXPOSE 80

ENTRYPOINT ["python3"]
CMD ["index.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
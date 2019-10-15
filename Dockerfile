FROM python:3.7.4-alpine3.10@sha256:488bfa82d8ac22f1ed9f1d4297613a920bf14913adb98a652af7dbbbf1c3cab9 AS base

# Don't write bytecode since containers are only executed once anyways
ENV PYTHONDONTWRITEBYTECODE 1
# Don't buffer stdout/-err. Supposedly improves output in Docker.
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ENTRYPOINT ["python", "/app/main.py"]

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./

# Both dev and prod require those.
RUN pipenv install --system --deploy

##########

FROM base AS dev

RUN pipenv install --system --dev

COPY . .

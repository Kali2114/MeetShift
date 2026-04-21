FROM python:3.12-alpine
LABEL maintainer="meetshift.com"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser -D -H django-user && \
    chown -R django-user:django-user /app

ENV PATH="/py/bin:$PATH"

USER django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

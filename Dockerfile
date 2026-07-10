FROM python:3.12-alpine
LABEL maintainer="meetshift.com"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt && \
    adduser -D -h /home/django-user django-user && \
    mkdir -p /app/staticfiles /app/media /app/logs /home/django-user /tmp && \
    chmod 1777 /tmp && \
    chown -R django-user:django-user /app /home/django-user

ENV PATH="/py/bin:$PATH"
ENV HOME=/home/django-user

USER django-user

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=5)"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# FROM python:3.7-slim
FROM python:3.7

WORKDIR /app
ENV HOME=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
COPY . .

USER 1001

ENTRYPOINT [ "python" ]

CMD [ "-m", "gunicorn", "--workers=1", "app", "-b", "0.0.0.0", "--log-level=debug" ]

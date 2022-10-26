FROM python:3.7-slim

WORKDIR /app
ENV HOME=/app
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt
COPY . .

USER 1001

ENTRYPOINT [ "python" ]

CMD [ "-m", "gunicorn", "--workers=1", "app", "-b", "0.0.0.0" ]

FROM python:3.11-slim

WORKDIR /app

COPY app.py config.py version.py ./
COPY templates ./templates

RUN pip install Flask

EXPOSE 80

CMD ["python", "app.py"] 

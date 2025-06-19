# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements (none for this simple app, but placeholder for future)
COPY app.py config.py ./
COPY templates ./templates

# Install Flask
RUN pip install Flask

# Expose port
EXPOSE 80

# Run the app
CMD ["python", "app.py"] 
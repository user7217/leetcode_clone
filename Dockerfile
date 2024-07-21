# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Flask and Docker SDK
RUN pip install flask docker

# Copy the Flask app code into the container
COPY app.py .

# Run the Flask app
CMD ["python", "app.py"]

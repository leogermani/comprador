
FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3-dev  build-essential python3-pip gunicorn
RUN pip install --upgrade setuptools
RUN pip install ez_setup

# Set the working directory in the container
WORKDIR /app

# Copy just the requirements file
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Mount the app directory as a volume
VOLUME /app

CMD ["gunicorn", "wa_webhook:app", "-b", "0.0.0.0:8000"]
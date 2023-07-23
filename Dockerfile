# Use the official Python image as the base image
FROM python:3.11.3-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory to the container's /app directory
COPY . .

# Expose the port your API server is running on 
EXPOSE 8080

# Start the API server 
CMD ["python", "apiserver.py"]
# Use Python 3.13 as base image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install flask pillow pytesseract requests

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]

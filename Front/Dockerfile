# Use a lightweight Python image without slim
FROM python:3.9

# Set the working directory
WORKDIR /appUser

# Copy requirements.txt and install dependencies
COPY requirements.txt /appUser/requirements.txt
RUN pip install --upgrade pip --no-cache-dir -r /appUser/requirements.txt

# Copy application code
COPY /app/ /appUser/app

# Set environment variable
ENV FLASK_ENV=production

# Expose the port that the app will run on
EXPOSE 5000

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.app:app"]
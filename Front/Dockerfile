FROM python:3.12
WORKDIR /appUser
COPY requirements.txt /appUser/requirements.txt
RUN pip install --upgrade pip --no-cache-dir -r /appUser/requirements.txt
RUN pip install --no-cache-dir mysql-connector-python
COPY /app/ /appUser/app
ENV FLASK_ENV=production
EXPOSE 5005
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "4", "app.app:app"]



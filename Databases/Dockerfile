FROM python:3.12-slim
WORKDIR /app_db
COPY requirements.txt /app_db/requirements.txt
RUN pip install --no-cache-dir -r /app_db/requirements.txt
COPY /app/ /app_db/app
EXPOSE 8000
RUN ls -l /app_db/app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

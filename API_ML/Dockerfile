
FROM python:3.12-slim
WORKDIR /app_ml
COPY requirements.txt /app_ml/requirements.txt
RUN pip install --no-cache-dir -r /app_ml/requirements.txt
COPY /app/ /app_ml/app
EXPOSE 8001
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8001"]

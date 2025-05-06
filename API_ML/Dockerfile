FROM python:3.12-slim
WORKDIR /app_ml
COPY requirements.txt /app_ml/requirements.txt
RUN pip install --no-cache-dir -r /app_ml/requirements.txt
COPY /app/ /app_ml/app
COPY /tests/ /app_ml/tests

EXPOSE 8001
# RUN pip install -U starlette
# RUN pytest 
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8001"]

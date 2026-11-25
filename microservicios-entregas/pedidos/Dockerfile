FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
# 1 worker: los pedidos viven en memoria y con más workers cada uno tendría su propia lista
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "--threads", "4", "app:app"]

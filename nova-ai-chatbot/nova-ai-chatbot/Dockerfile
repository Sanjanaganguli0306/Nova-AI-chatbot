FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HTTPS=0 DATA_DIR=/data
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && useradd --system --no-create-home --shell /usr/sbin/nologin nova
COPY . .
# Code is read-only; the app can only write its database and generated key under /data.
RUN mkdir -p /data && chown nova:nova /data && chmod -R a-w /app
VOLUME /data
USER nova
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
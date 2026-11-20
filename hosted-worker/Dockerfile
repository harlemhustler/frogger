FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir Pillow==11.3.0
COPY FROGGER/frogger.py FROGGER/frogger.py
COPY hosted-worker/server.py hosted-worker/server.py
USER 65534:65534
EXPOSE 8080
CMD ["python", "hosted-worker/server.py"]

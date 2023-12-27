FROM python:3.11-alpine

WORKDIR /app

COPY models models
COPY routers routers
COPY schemas schemas
COPY utils utils
COPY database.py .
COPY main.py .
COPY requirements.txt .

RUN apk add --no-cache libffi-dev gcc musl-dev
RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]
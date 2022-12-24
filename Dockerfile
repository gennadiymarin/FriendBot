FROM python:3.9

WORKDIR /bot2.0

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./source ./source

CMD ["python", "./source/main.py"]
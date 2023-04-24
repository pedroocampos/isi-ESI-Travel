FROM python:3.8

RUN mkdir /micro
WORKDIR /micro
ADD . /micro/
COPY src/static /micro/static
COPY src/instance /micro/instance
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/micro/src/app.py"]
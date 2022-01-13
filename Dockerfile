FROM python:3.9.9-alpine

WORKDIR /usr/src/app 
ADD requirements.txt .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

#EXPOSE 8090

CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8090" ]
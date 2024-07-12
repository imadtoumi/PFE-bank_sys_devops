FROM python:3.9.2

WORKDIR bank_docker

COPY docker/requirments.txt requeirments.txt 

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirments.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]


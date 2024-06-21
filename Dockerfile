FROM python:3.10-slim

WORKDIR /answer_machine/app

COPY ./requirements.txt /answer_machine/requirements.txt

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r /answer_machine/requirements.txt

COPY ./app /answer_machine/app

CMD ["python", "main.py"]
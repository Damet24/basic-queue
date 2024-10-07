FROM python:3.12

EXPOSE 8080
ADD requirements.txt .
RUN pip install -r ./requirements.txt
CMD ["python", "/app/main.py"]
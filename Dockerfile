FROM python:3.9-slim-buster as production
WORKDIR app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ["app.py", "handlers.py", "./"]
ENV FLASK_ENV=development
EXPOSE 5000
CMD ["python", "app.py"]


FROM production as test
COPY ["test_handlers.py", "dev-requirements.txt", "./"]
RUN pip install -r dev-requirements.txt
CMD ["pytest"]


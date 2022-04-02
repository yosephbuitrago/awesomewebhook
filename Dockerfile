FROM python:3.9-slim-buster as production
WORKDIR app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py app.py
COPY repoconfig.py repoconfig.py
ENV FLASK_ENV=development
EXPOSE 5000
CMD ["python", "app.py"]


FROM production as test
RUN pip install pytest==7.1.1
COPY test_repoconfig.py test_repoconfig.py
CMD ["pytest"]


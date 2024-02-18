FROM python:3.9-slim

WORKDIR /src

COPY requirements/production.txt ./requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY rosatom-quizzes-google-sheets.json ./
COPY rosatom_quizzes_bot ./rosatom_quizzes_bot

ENTRYPOINT [ "python", "-m" ]
CMD [ "rosatom_quizzes_bot" ]
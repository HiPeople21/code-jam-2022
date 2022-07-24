FROM python:3.10-slim-bullseye

WORKDIR sirenity
RUN useradd -ms /bin/bash sirenity
USER sirenity
COPY . .

EXPOSE 8000
RUN pip install .

CMD python -m sirenity

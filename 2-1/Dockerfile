FROM python:3.7
RUN pip install flask gunicorn
RUN mkdir /app
COPY hola_flask.py /app
WORKDIR /app
EXPOSE 5000
CMD ["/usr/local/bin/gunicorn", "-b",  "0.0.0.0:5000", "-w", "4", "hola_flask:app"]
# Set base image as python
FROM python

# Add env variable for query
ENV QUERY "$QUERY"
ENV TIME "$TIME"
ENV MAX_RESULTS "$MAX_RESULTS"
ENV HOST "$HOST"
ENV PORT "$PORT"

# Update and install dependencies
RUN apt update -y
RUN apt upgrade -y
RUN apt install vim python3-pip libpq-dev python3-dev -y && pip3 install --upgrade pip

# Setting up Flask app
COPY ../app/ app/
COPY ../model/ model/
COPY ../.env .env
COPY ../requirements.txt requirements.txt
RUN pip3 install --no-deps -r requirements.txt

# Run the app
CMD python3 app/app.py --query "$QUERY" --time-interval-minutes "$TIME" --max-results "$MAX_RESULTS" --host "$HOST" --port "$PORT"
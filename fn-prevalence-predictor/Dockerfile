FROM jonduckworthdg/geopandas-base

RUN mkdir -p /app

COPY ./fwatchdog /usr/bin
RUN chmod +x /usr/bin/fwatchdog

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY index.py .
COPY config.py .
COPY preprocess_helpers.py .
COPY function function

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
ENV fprocess="python index.py"
# Set to true to see request in function logs
ENV write_debug="false"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1
CMD [ "fwatchdog" ]

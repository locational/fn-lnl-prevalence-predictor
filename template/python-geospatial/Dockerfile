FROM jonduckworthdg/geopandas-base

RUN wget https://github.com/openfaas/faas/releases/download/0.9.14/fwatchdog -O /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

RUN mkdir -p /app/function

WORKDIR /app

COPY function/requirements.txt function/
RUN pip install -r function/requirements.txt

COPY index.py .
COPY config.py .
COPY preprocess_helpers.py .
COPY function function

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
ENV fprocess="python index.py"
# Set to true to see request in function logs
# ENV write_debug="false"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1
CMD [ "fwatchdog" ]

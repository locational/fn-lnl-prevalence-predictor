FROM disarm/geopandas-r-base:1.0.0

RUN apt-get install curl -y \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSL https://github.com/openfaas/faas/releases/download/0.9.14/fwatchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog \
    && cp /usr/bin/fwatchdog /home/app \
    && apt-get remove curl -y

RUN mkdir -p /app

# COPY ./fwatchdog /usr/bin
# RUN chmod +x /usr/bin/fwatchdog

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY index.py .
COPY config.py .
COPY preprocess_helpers.py .
COPY function function
RUN pip install -r function/requirements.txt


# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
ENV fprocess="python index.py"
# Set to true to see request in function logs
ENV combine_output='false'
# ENV write_debug="true"
ENV write_timeout=600
ENV read_timeout=600
ENV exec_timeout=600

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1
CMD [ "fwatchdog" ]

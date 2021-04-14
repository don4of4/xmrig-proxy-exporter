FROM python:3-slim

COPY . /xmrig_proxy_exporter

RUN pip install /xmrig_proxy_exporter && cp /usr/local/bin/xmrig-proxy-exporter /xmrig-proxy-exporter

EXPOSE 9189

ENTRYPOINT ["/xmrig-proxy-exporter"]

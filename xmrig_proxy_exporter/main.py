import argparse
import http.server
import logging
import sys

import prometheus_client
from prometheus_client import start_http_server

from .xmrig_collector import XmrigCollector
from .xmrig_proxy_collector import XmrigProxyCollector

def main():
    parser = argparse.ArgumentParser("xmrig-proxy-exporter")
    # Bindings
    parser.add_argument("--port", type=int, default=9189)
    parser.add_argument("--bind_address", default="0.0.0.0")
    # Collector Information
    parser.add_argument("--proxy-mode", action='store_true')
    parser.add_argument("--url", required=True)
    parser.add_argument("--token")
    # Options
    parser.add_argument("--verbose", "-v", action="count")

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(stream=sys.stdout, level=level)

    # Xmrig Collector
    if args.proxy_mode:
        collector = XmrigProxyCollector(args.url, token=args.token)
    else:
        collector = XmrigCollector(args.url, token=args.token)

    # Register the collector
    prometheus_client.REGISTRY.register(collector)

    # Setup handler
    #handler = prometheus_client.MetricsHandler.factory(prometheus_client.REGISTRY)

    start_http_server(args.port)
    input()
    
    # Bind server and start
    #server = http.server.HTTPServer((args.bind_address, args.port), handler)
    #server.serve_forever()



if __name__ == '__main__':
    main()
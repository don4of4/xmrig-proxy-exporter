import prometheus_client
import requests


class XmrigCollector(object):

    def __init__(self, url, token=None):
        self.url = url
        self.token = token
        self._prefix = "xmrig_"

    def make_metric(self, is_counter, _name, _documentation, _value, **_labels):
        label_names = list(_labels.keys())
       
        # Select the type of data
        if is_counter:
            cls = prometheus_client.core.CounterMetricFamily
        else:
            cls = prometheus_client.core.GaugeMetricFamily
        
        # Create the metrics
        metric = cls(_name, _documentation or "No Documentation", labels=label_names)
        metric.add_metric([str(_labels[k]) for k in label_names], _value)
        
        return metric

    def collect(self):
        metrics = []
        headers = {}
        
        # If there is a token, add it to the request header
        if self.token:
            headers["Authorization"] = "Bearer " + self.token


        j = requests.get(self.url, headers=headers).json()
        ids = {"worker_id": j["worker_id"]}

        # Loop through total
        for i, v in enumerate(j["hashrate"]["total"]):
            if not v is None:
                metrics.append(self.make_metric(
                    False,
                    self._prefix + "hashrate%d" % i,
                    "Overall Hashrate",
                    v,
                    **ids))

        # Loop through threads
        for tidx, t in enumerate(j["hashrate"]["threads"]):
            for i, v in enumerate(t):
                if not v is None:
                    labels = {"thread": tidx}
                    labels.update(ids)
                    metrics.append(self.make_metric(
                        False,
                        self._prefix + "thread_hashrate%d" % i,
                        "Thread Hashrate",
                        v,
                        **labels))
        
        # Create metrics
        metrics.append(self.make_metric(
            False,
            self._prefix + "diff_current",
            "Current Difficulty",
            j["results"]["diff_current"],
            **ids))
        metrics.append(self.make_metric(
            True,
            self._prefix + "shares_good",
            "Good Shares",
            j["results"]["shares_good"],
            **ids))
        metrics.append(self.make_metric(
            True,
            self._prefix + "shares_total",
            "Total Shares",
            j["results"]["shares_total"],
            **ids))
        metrics.append(self.make_metric(
            False,
            self._prefix + "avg_time",
            "Average Time",
            j["results"]["avg_time"],
            **ids))
        metrics.append(self.make_metric(
            True,
            self._prefix + "hashes_total",
            "Total Hashes",
            j["results"]["hashes_total"],
            **ids))
        metrics.append(self.make_metric(
            False,
            self._prefix + "best",
            "Best",
            j["results"]["best"][0],
            **ids))
        metrics.append(self.make_metric(
            True,
            self._prefix + "errors",
            "Count of errors",
            len(j["results"]["error_log"]),
            **ids))
        metrics.append(self.make_metric(
            False,
            self._prefix + "connection_uptime",
            "Connection uptime",
            j["connection"]["uptime"],
            **ids))
        metrics.append(self.make_metric(
            False,
            self._prefix + "connection_ping",
            "Connection ping",
            j["connection"]["ping"],
            **ids))
        metrics.append(self.make_metric(
            True,
            self._prefix + "connection_failures",
            "Connection failures",
            j["connection"]["failures"],
            **ids))
            
        return metrics

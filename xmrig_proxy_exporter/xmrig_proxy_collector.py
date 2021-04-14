#import prometheus_client
import prometheus_client.core
import requests


class XmrigProxyCollector(object):

    def __init__(self, url, token=None):
        self.url = url
        self.token = token
        self._prefix = "xmrig_proxy_"


    def collect(self):
        metrics = []

        for metric in self._collect_pages():
            metrics.append(metric)

        return metrics

    def _make_metric(self, is_counter, _name, _documentation, _value, **_labels):
        label_names = list(_labels.keys())
        
        # Select the type of data 
        if is_counter:
            c = prometheus_client.core.CounterMetricFamily
        else:
            c = prometheus_client.core.GaugeMetricFamily
        
       
        # Create the metrics
        _documentation = _documentation or "No Documentation"
        metric = c(_name, _documentation, labels=label_names)
        metric.add_metric([str(_labels[k]) for k in label_names], _value)
        
        return metric

    
    def _collect_pages(self):
        headers = {}
        metrics = []

        # Create a auth bearer token      
        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        get_request = requests.get(self.url + 'summary', headers=headers)
        
        # Check response code
        if (get_request.status_code != 200):
            printerr ('Error: Non-200 response: '+get_request.status_code)

        json = get_request.json()

        ids = {"worker_id": json["worker_id"], "kind": json['kind']}

        # Global metrics
        metrics.append(self._make_metric(
            False,
            self._prefix + "miners",
            "Miners (count)",
            json['miners']['now'], **ids))
        
        metrics.append(self._make_metric(
            True,
            self._prefix + "uptime",
            "Uptime (Seconds)",
            json['uptime'], **ids))
        
        metrics.append(self._make_metric(
            False,
            self._prefix + "load",
            "Load",
            json['resources']['load_average'][0], **ids))

        metrics.append(self._make_metric(
            False,
            self._prefix + "memory_free",
            "Free Memory (bytes)",
            json['resources']['memory']['free'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "memory_total",
            "Total Memory (bytes)",
            json['resources']['memory']['total'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "memory_residentsetmemory",
            "Resident Set Memory (bytes)",
            json['resources']['memory']['resident_set_memory'], **ids))


        # UpStreams:        
        metrics.append(self._make_metric(
            False,
            self._prefix + "upstreams_active",
            "Active Upstreams",
            json['upstreams']['active'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "upstreams_sleep",
            "Sleeping Upstreams",
            json['upstreams']['sleep'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "upstreams_error",
            "Error Upstreams",
            json['upstreams']['error'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "upstreams_total",
            "Total Upstreams",
            json['upstreams']['total'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "upstreams_ratio",
            "Ratio of Workers to Upstreams",
            json['upstreams']['ratio'], **ids))

        # Results
        metrics.append(self._make_metric(
            False,
            self._prefix + "shares_accepted",
            "Accepted Shares",
            json['results']['accepted'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "shares_rejected",
            "Rejected Shares",
            json['results']['rejected'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "shares_invalid",
            "Invalid Shares",
            json['results']['invalid'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "shares_expired",
            "Expired Shares",
            json['results']['expired'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "results_avgtime",
            "Avg Results Time",
            json['results']['avg_time'], **ids))
        metrics.append(self._make_metric(
            False,
            self._prefix + "results_latency",
            "Results Latency",
            json['results']['latency'], **ids))
        metrics.append(self._make_metric(
            True,
            self._prefix + "hashes_total",
            "Total Hashes",
            json['results']['hashes_total'], **ids))
        metrics.append(self._make_metric(
            True,
            self._prefix + "hashes_donate",
            "Donated Hashes",
            json['results']['hashes_donate'], **ids))

        # Hashrate
        labels = ['1m','10m','1h','12h','24h','all']
        for num, value in enumerate(json['hashrate']['total']):
            metrics.append(self._make_metric(
                False,
                self._prefix + "hashrate_{0}".format(labels[num]),
                "Hashrate ({0})".format(labels[num]),
                json['hashrate']['total'][num], **ids))


        # Add in workers data
        for metric in self.collect_workers(ids):
            metrics.append(metric)

        return metrics

    def collect_workers(self, ids):
        headers = {}
        metrics = []

        # Create a auth bearer token      
        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        get_request = requests.get(self.url + 'workers', headers=headers)
        
        # Check response code
        if (get_request.status_code != 200):
            printerr ('Error: Non-200 response: '+get_request.status_code)

        json = get_request.json()

        # Workers
        labels = ['workername','last_ip','active_nodes','accepted_shares','rejected_shares','invalid_shares','hashes','unk','hashrate_1m','hashrate_10m','hashrate_1h','hashrate_12h','hashrate_24h','hashrate_all']
        documentation = ['Worker Name', 'Last Ip', 'Active Nodes', 'Accepted Shares', 'Requested Shares', 'Invalid Shares', 'Hashes', 'UNK', 'Hashrate (1m)', 'Hashrate (10m)', 'Hashrate (1h)','Hashrate (12h)', 'Hashrate (24h)', 'Hashrate (all)']
        isCounter = [False,False,False,False,False,False,True,True,False,False,False,False,False,False]
        for worker_idx, worker in enumerate(json['workers']):
            
            # Label the worker metrics
            ids['workername'] = worker[0]

            for num, value in enumerate(worker):
                if num < 2:
                    continue   
                #if type(value)== string:
                #    print("{0} {1}".format(value,type(value)))
                metrics.append(self._make_metric(
                    isCounter[num],
                    self._prefix + "worker_{0}_{1}".format(worker[0],labels[num]),
                    "Hashrate ({0})".format(documentation[num]),
                    value, **ids))

        # Cleanup
        ids.pop('workername', None)

        return metrics



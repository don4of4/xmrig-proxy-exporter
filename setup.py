import setuptools

setuptools.setup(
    name="xmrig-proxy-exporter",
    version="0.1.0",
    author="Don Scott",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.18.4",
        "prometheus_client>=0.8.0,<=0.10.1",
    ],
    entry_points={
        "console_scripts": [
            "xmrig-proxy-exporter = xmrig_proxy_exporter:main",
        ],
    },
)

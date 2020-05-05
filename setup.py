import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hss_server",
    version="0.0.3",
    author="Patrick Fial",
    author_email="mg.m@gmx.net",
    description="Python-based skill server for the hermes MQTT protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/patrickjane/hss-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
       'rpyc',
       'paho-mqtt',
       'requests',
       'appdirs',
       'GitPython'
    ],
    scripts=['scripts/hss_server', 'scripts/hss_cli'],
    python_requires='>=3.6',
)

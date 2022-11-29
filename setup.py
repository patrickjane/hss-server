import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hss_server",
    version="0.5.4",
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
       'amqtt',
       'requests',
       'appdirs',
       'GitPython',
       'pid'
    ],
    scripts=['scripts/hss-server', 'scripts/hss-cli'],
    python_requires='>=3.7',
)

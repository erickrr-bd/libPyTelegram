# ⌯⌲ libPyTelegram v2.2

A lightweight Python library for sending Telegram messages using PyCurl.

libPyTelegram is a lightweight library written in Python that makes it easy to send messages over Telegram using PyCurl. It's designed to easily integrate into automated scripts, monitoring flows, and environments where Telegram is used as the primary channel for technical communication or alerts. 

# 🚀 Characteristics
- Sending messages to Telegram channels.
- Sending messages with files attached to Telegram channels.
- Easy integration into monitoring scripts, CI/CD pipelines and auditing tools.

# 🧱 Requirements
- Python 3.12+
- Python Libraries
  - [pycurl](https://pycurl.io/)

# Installation

Copy the "libPyTelegram" folder to the following path:

`/usr/local/lib/python3.9/site-packages`

**NOTE:** The path depends on the Python version.

# ⚠️ Possible Issues

When using the latest version of PyCurl , in certain situations it's possible to get the following error:

`ImportError: pycurl: libcurl link-time ssl backend (openssl) is different from compile-time ssl backend (none/other)`

To resolve this possible error, you must first uninstall PyCurl and define the following environment variable:

`export PYCURL_SSL_LIBRARY=openssl`

Once the above is done, it's required to reinstall PyCurl on the system:

`pip3 install pycurl`

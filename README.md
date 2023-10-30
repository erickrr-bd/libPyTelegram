# libPyTelegram v1.2

Easy sending messages via Telegram with Pycurl.

## Characteristics
- Sending a text message via Telegram.
- Sending a text message with an attached file via Telegram.

# Requirements
- CentOS 8, Red Hat 8 or Rocky Linux 8
- Python 3.9
- Python Libraries
  - pycurl <= 7.45.2 (It's recommended to use the latest version specified)
    
# Installation

Copy the "libPyTelegram" folder to the following path:

`/usr/local/lib/python3.9/site-packages`

**NOTE:** The path depends on the Python version.

# Issues

When using the latest version of PyCurl, the following error may be displayed:

`ImportError: pycurl: libcurl link-time ssl backend (openssl) is different from compile-time ssl backend (none/other)`

To solve it, the following commands must be executed (first uninstall PyCurl, if it's installed):

`export PYCURL_SSL_LIBRARY=openssl`

`pip3 install pycurl`

# Commercial Support
![Tekium](https://github.com/unmanarc/uAuditAnalyzer2/blob/master/art/tekium_slogo.jpeg)

Tekium is a cybersecurity company specialized in red team and blue team activities based in Mexico, it has clients in the financial, telecom and retail sectors.

Tekium is an active sponsor of the project, and provides commercial support in the case you need it.

For integration with other platforms such as the Elastic stack, SIEMs, managed security providers in-house solutions, or for any other requests for extending current functionality that you wish to see included in future versions, please contact us: info at tekium.mx

For more information, go to: https://www.tekium.mx/

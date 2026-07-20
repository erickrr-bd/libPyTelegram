# libPyTelegram (v2.3)

A high-performance, lightweight Python utility module designed for broadcasting alerts, system status updates, and files via the **Telegram Bot API**. Built on top of `pycurl`, this module ensures low-overhead HTTP connection handling, making it an ideal choice for background automation scripts, DevOps monitoring, and terminal-based user interfaces (TUI/dialog).

---

## Features

* 🚀 **Low Overhead:** Leverages `pycurl` for rapid, stable HTTP transport execution.
* 💬 **Text Broadcasting:** Dispatches raw text messages seamlessly using the Telegram `sendMessage` endpoint.
* 📁 **Document Streaming:** Transmits logs, reports, or configuration backups via multipart form uploads (`sendDocument`).
* 🖥️ **TUI Friendly:** Safely isolates HTTP response handling via memory buffers to prevent terminal corruption in `ncurses` or `dialog` environments.

---

# 📝 Requirements
- Python 3.12+
- Python Libraries
  - [pycurl](https://pycurl.io/)

# 🛠️ Installation

The installation can be done using a .whl (Wheel) file. To generate a file, you must have the following packaging tools installed:

`pip install setuptools wheel`

The following command is executed from the root of the project:

`python setup.py sdist bdist_wheel`

This action will generate the following files:

`dist/libPyTelegram-2.2-py3-none-any.whl`

`dist/libPyTelegram-2.2.tar.gz`

It's now possible to install the library using the Wheel file and the pip tool:

`pip3 install libPyTelegram-2.2-py3-none-any.whl`

---

API Reference
send_telegram_message
Sends a standard text notification to a specific Chat ID.

```python
def send_telegram_message(self, telegram_bot_token: str, telegram_chat_id: str, telegram_message: str) -> int:
```
Parameters:

telegram_bot_token (str): Unique token issued by the @BotFather.

telegram_chat_id (str): Target channel or user identifier destination.

telegram_message (str): The text payload to be transmitted.

Returns:

response_http_code (int): Returns 200 on success, or the corresponding HTTP error code.

send_telegram_message_and_file
Uploads a document attached with a descriptive caption text.

```python
def send_telegram_message_and_file(self, telegram_bot_token: str, telegram_chat_id: str, telegram_message: str, file: str) -> int:
```
Parameters:

telegram_bot_token (str): Unique token issued by the @BotFather.

telegram_chat_id (str): Target channel or user identifier destination.

telegram_message (str): Text payload sent as the document's caption.

file (str): Absolute or relative local path to the file.

Returns:

response_http_code (int): Returns 200 on success, or the corresponding HTTP error code.

---

Code Example
Here is a straightforward implementation showing how to initialize and use the module within your main utility workflow:

```python
from libPyTelegram import libPyTelegram

# Initialize the messenger subsystem
notifier = libPyTelegram()

TOKEN = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
CHAT_ID = "987654321"

# 1. Dispatching a routine text alert
status_code = notifier.send_telegram_message(
    telegram_bot_token=TOKEN,
    telegram_chat_id=CHAT_ID,
    telegram_message="🔒 [INFO] Snapshot rotation triggered successfully."
)

if status_code == 200:
    print("Notification transmitted successfully.")

# 2. Uploading a compressed log file
file_status_code = notifier.send_telegram_message_and_file(
    telegram_bot_token=TOKEN,
    telegram_chat_id=CHAT_ID,
    telegram_message="📁 [BACKUP] Attached system logs for cluster analytics.",
    file="/var/log/snap_tool/execution_report.log"
)
```

---

# ⚠️ Possible Issues

When using the latest version of PyCurl , in certain situations it's possible to get the following error:

`ImportError: pycurl: libcurl link-time ssl backend (openssl) is different from compile-time ssl backend (none/other)`

To resolve this possible error, you must first uninstall PyCurl and define the following environment variable:

`export PYCURL_SSL_LIBRARY=openssl`

Once the above is done, it's required to reinstall PyCurl on the system:

`pip3 install pycurl`

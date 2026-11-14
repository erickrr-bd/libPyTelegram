# libPyTelegram

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-2.3-green)

A minimal and robust Python wrapper around the [Telegram Bot API](https://core.telegram.org/bots/api) built on **PycURL**. It sends text messages and files to a chat, with hardened TLS settings, input validation, timeouts and automatic retries.

It does one thing, `sendMessage` and `sendDocument`, and tries to do it safely. It is used by [CVE-Alert](https://github.com/erickrr-bd/CVE-Alert) to deliver its notifications.

## Features

- Send a **text message** (`sendMessage`) or a **file with a caption** (`sendDocument`).
- **Strict TLS**: certificate and host verification, TLS 1.2 or newer, HTTPS only, redirects are never followed.
- **Timeouts** on every request (connect, request and upload).
- **Input validation** before any network traffic: bot token format, chat ID format, file existence, location and size.
- **Automatic retries** for HTTP `429` (honouring Telegram's `retry_after`) and `5xx`, with exponential backoff.
- **The token never leaks** through error messages: it is replaced by `<TOKEN>`.
- **Connection reuse** (keep-alive) through a single PycURL handle, released with `close()` or a `with` block.
- Messages and captions are truncated to Telegram's limits instead of being rejected.
- Optional `allowed_dir` so only files inside a given directory can be sent.

## Requirements

| Requirement | Notes |
| --- | --- |
| Python | 3.10 or newer |
| [PycURL](https://pypi.org/project/pycurl/) | `pip install pycurl` (needs libcurl; building from source may also need the libcurl and OpenSSL development packages) |

## Installation

```bash
git clone https://github.com/erickrr-bd/libPyTelegram.git
pip install pycurl
```

Copy `libPyTelegram.py` into your project, or add the cloned folder to your `PYTHONPATH`.

## Quick start

### Send a message

```python
from libPyTelegram import libPyTelegram

with libPyTelegram() as telegram:
	code = telegram.send_telegram_message("123456789:AAH...", "-1001234567890", "Hello from libPyTelegram")

if code == 200:
	print("Message sent")
else:
	print(f"Telegram returned HTTP {code}: {telegram.last_response_body}")
```

### Send a file

```python
with libPyTelegram(allowed_dir = "/var/reports") as telegram:
	code = telegram.send_telegram_message_and_file(token, chat_id, "Daily report", "/var/reports/report.pdf")
```

The message is sent as the **caption** of the document.

### Handle errors

```python
try:
	code = telegram.send_telegram_message(token, chat_id, message)
except ValueError:
	...   # invalid token or chat ID format (or file larger than 50 MB)
except ConnectionError:
	...   # network / TLS error (the token is redacted in the message)
```

## API reference

### `libPyTelegram(allowed_dir = None, max_retries = 3)`

| Parameter | Description |
| --- | --- |
| `allowed_dir` | If set, only files inside this directory can be sent with `send_telegram_message_and_file`. |
| `max_retries` | How many times a `429` or `5xx` response is retried. `0` disables retries. |

### Methods

| Method | Returns | Description |
| --- | --- | --- |
| `send_telegram_message(telegram_bot_token, telegram_chat_id, telegram_message)` | `int` | Sends a text message. Messages longer than 4096 characters are truncated. |
| `send_telegram_message_and_file(telegram_bot_token, telegram_chat_id, telegram_message, file)` | `int` | Sends a file; `telegram_message` is its caption (truncated to 1024 characters). The file must exist, be at most 50 MB and, if `allowed_dir` is set, be inside it. |
| `close()` | `None` | Releases the underlying PycURL handle. Called automatically by the `with` statement. |

Both send methods **return the HTTP status code** of the Telegram API. The response body of the last request is available in `last_response_body` (useful to read the `description` of an error).

Messages are sent as **plain text** (no `parse_mode`), so characters such as `<`, `&` or `_` never need escaping and cannot break the message.

### Accepted values

| Value | Rule |
| --- | --- |
| Bot token | `<digits>:<hash>`: 5 or more digits, a colon, and 30 or more letters, digits, `_` or `-` |
| Chat ID | An integer (negative for groups and channels, for example `-1001234567890`) or a public `@channel` name |
| File | An existing regular file, at most 50 MB, inside `allowed_dir` when it is set |

### Exceptions

| Exception | When |
| --- | --- |
| `ValueError` | Invalid token or chat ID format, or a file larger than 50 MB. |
| `FileNotFoundError` | The file to send does not exist. |
| `PermissionError` | The file is outside `allowed_dir`. |
| `ConnectionError` | PycURL could not complete the request (DNS, connection, TLS, timeout...). The token is replaced by `<TOKEN>` in the message. |

### HTTP codes you will usually see

| Code | Meaning |
| --- | --- |
| `200` | Message accepted. |
| `400` | Bad request. It can be a problem of the message or of the chat (for example `chat not found`): read `last_response_body`. |
| `401` | Invalid bot token. |
| `403` | The bot was blocked, removed from the chat, or has no permission to write in it. |
| `404` | Token not found, or wrong method. |
| `429` | Too many requests (retried automatically up to `max_retries` times). |

### Settings

These class attributes can be changed on the class or on an instance:

| Attribute | Default | Description |
| --- | --- | --- |
| `MAX_MESSAGE_LENGTH` | `4096` | Maximum characters of a message. |
| `MAX_CAPTION_LENGTH` | `1024` | Maximum characters of a caption. |
| `MAX_FILE_SIZE` | 50 MB | Maximum size of a file. |
| `CONNECT_TIMEOUT` | `10` s | Time allowed to establish the connection. |
| `REQUEST_TIMEOUT` | `30` s | Total time allowed for a message request. |
| `UPLOAD_TIMEOUT` | `120` s | Total time allowed for a file upload. |
| `MAX_RETRY_WAIT` | `60` s | Maximum wait between retries. |

## Retries

When Telegram answers `429` or any `5xx`, the request is repeated up to `max_retries` times:

- On `429`, the wait is the `retry_after` value Telegram sends in the response, if present.
- Otherwise the wait doubles on every attempt (1 s, 2 s, 4 s...).
- No wait is longer than `MAX_RETRY_WAIT`.
- Network-level failures (`ConnectionError`) are **not** retried.

The wait uses `time.sleep`, so it **cannot be interrupted**. In a daemon that must stop quickly (for example when systemd sends `SIGTERM`), create the client with `max_retries = 0` and handle `429` and `5xx` in your own loop.

## Security notes

- The Telegram API requires the token to be part of the URL path. This library never logs it and removes it from error messages, but **do not log the URLs or exceptions of other layers** (proxies, debug output of other libraries) without checking them.
- TLS verification cannot be disabled, only HTTPS is allowed, and redirects are not followed.
- Use `allowed_dir` whenever the path of the file to send comes from configuration or user input, so it cannot be used to exfiltrate arbitrary files.
- Telegram limits how fast a bot can write (roughly one message per second per chat and about 20 messages per minute in a group; see the [Bots FAQ](https://core.telegram.org/bots/faq)). When you send many messages in a row, pause between them.
- Store the bot token encrypted and out of version control. [libPyAgentConfiguration](https://github.com/erickrr-bd/libPyAgentConfiguration) and [libPyUtils](https://github.com/erickrr-bd/libPyUtils) provide that for the CVE-Alert suite.
- **Thread safety:** one PycURL handle is reused between calls, so an instance is **not thread-safe**. Use one instance per thread.

## Author

**Erick Roberto Rodriguez Rodriguez**
[erodriguez@tekium.mx](mailto:erodriguez@tekium.mx) · [erickrr.tbd93@gmail.com](mailto:erickrr.tbd93@gmail.com) · [GitHub](https://github.com/erickrr-bd/libPyTelegram)

# ⚠️ Possible Issues

When using the latest version of PyCurl , in certain situations it's possible to get the following error:

`ImportError: pycurl: libcurl link-time ssl backend (openssl) is different from compile-time ssl backend (none/other)`

To resolve this possible error, you must first uninstall PyCurl and define the following environment variable:

`export PYCURL_SSL_LIBRARY=openssl`

Once the above is done, it's required to reinstall PyCurl on the system:

`pip3 install pycurl`

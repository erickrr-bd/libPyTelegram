"""
Author: Erick Roberto Rodriguez Rodriguez
Email: erodriguez@tekium.mx, erickrr.tbd93@gmail.com
GitHub: https://github.com/erickrr-bd/libPyTelegram
libPyTelegram v2.3 - July 2026
A minimal and robust Python wrapper around the Telegram Bot API using PycURL.

Hardened revision: explicit TLS settings, input validation, timeouts,
guaranteed resource cleanup, handle reuse and retries for 429/5xx.
"""
import re
import json
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from pycurl import Curl, HTTP_CODE, FORM_FILE, error as PycurlError


class libPyTelegram:

	# Telegram API limits
	MAX_MESSAGE_LENGTH = 4096
	MAX_CAPTION_LENGTH = 1024
	MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

	# Network settings
	CONNECT_TIMEOUT = 10
	REQUEST_TIMEOUT = 30
	UPLOAD_TIMEOUT = 120
	MAX_RETRY_WAIT = 60

	_TOKEN_RE = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{30,}$")
	_CHAT_ID_RE = re.compile(r"^(-?\d+|@[A-Za-z0-9_]{5,})$")

	def __init__(self, allowed_dir: str | None = None, max_retries: int = 3) -> None:
		"""
		Constructor.

		Parameters:
			allowed_dir (str | None): If set, only files inside this directory can be sent.
			max_retries (int): Retries for HTTP 429 and 5xx responses (0 disables retries).

		Note:
			The internal PycURL handle is reused between calls (keep-alive), so an
			instance is NOT thread-safe. Use one instance per thread.
		"""
		self._curl = Curl()
		self._allowed_dir = Path(allowed_dir).resolve() if allowed_dir else None
		self._max_retries = max(0, max_retries)
		self.last_response_body = ""


	def close(self) -> None:
		"""
		Method that releases the underlying PycURL handle.
		"""
		self._curl.close()


	def __enter__(self) -> "libPyTelegram":
		return self


	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.close()


	def send_telegram_message(self, telegram_bot_token: str, telegram_chat_id: str, telegram_message: str) -> int:
		"""
		Method that sends a text message via Telegram.

		Parameters:
			telegram_bot_token (str): Telegram Bot Token.
			telegram_chat_id (str): Telegram Chat ID.
			telegram_message (str): Message to send.

		Returns:
			response_http_code (int): HTTP code returned by the Telegram API.
			The response body is available in `last_response_body`.
		"""
		self._validate_token(telegram_bot_token)
		self._validate_chat_id(telegram_chat_id)
		telegram_message = telegram_message[:self.MAX_MESSAGE_LENGTH]
		url = self._build_url(telegram_bot_token, "sendMessage")
		post_fields = urlencode({"chat_id": telegram_chat_id, "text": telegram_message})

		def configure(curl: Curl) -> None:
			curl.setopt(curl.POSTFIELDS, post_fields)
			curl.setopt(curl.TIMEOUT, self.REQUEST_TIMEOUT)

		return self._request(url, telegram_bot_token, configure)


	def send_telegram_message_and_file(self, telegram_bot_token: str, telegram_chat_id: str, telegram_message: str, file: str) -> int:
		"""
		Method that sends a text message and a file via Telegram.

		Parameters:
			telegram_bot_token (str): Telegram Bot Token.
			telegram_chat_id (str): Telegram Chat ID.
			telegram_message (str): Message to send.
			file (str): File's path.

		Returns:
			response_http_code (int): HTTP code returned by the Telegram API.
			The response body is available in `last_response_body`.
		"""
		self._validate_token(telegram_bot_token)
		self._validate_chat_id(telegram_chat_id)
		path = self._validate_file(file)
		telegram_message = telegram_message[:self.MAX_CAPTION_LENGTH]
		url = self._build_url(telegram_bot_token, "sendDocument")
		data = [("chat_id", telegram_chat_id), ("document", (FORM_FILE, str(path))), ("caption", telegram_message)]

		def configure(curl: Curl) -> None:
			curl.setopt(curl.HTTPPOST, data)
			curl.setopt(curl.TIMEOUT, self.UPLOAD_TIMEOUT)

		return self._request(url, telegram_bot_token, configure)


	def _request(self, url: str, token: str, configure) -> int:
		"""
		Method that performs the request with TLS hardening, timeouts and retries.

		Parameters:
			url (str): Full API URL (contains the token, never log it).
			token (str): Bot token, used only to redact error messages.
			configure (callable): Function that sets the request-specific options.

		Returns:
			response_http_code (int): HTTP code returned by the Telegram API.
		"""
		attempt = 0
		while True:
			storage = BytesIO()
			try:
				self._curl.reset()
				self._apply_secure_options(url)
				configure(self._curl)
				self._curl.setopt(self._curl.WRITEFUNCTION, storage.write)
				self._curl.perform()
				response_http_code = self._curl.getinfo(HTTP_CODE)
				self.last_response_body = storage.getvalue().decode("utf-8", errors="replace")
			except PycurlError as exception:
				# Make sure the token never leaks through an error message.
				message = str(exception).replace(token, "<TOKEN>")
				raise ConnectionError(f"Telegram request failed: {message}") from None
			finally:
				storage.close()

			retryable = response_http_code == 429 or 500 <= response_http_code < 600
			if not retryable or attempt >= self._max_retries:
				return response_http_code

			time.sleep(self._retry_delay(response_http_code, attempt))
			attempt += 1


	def _apply_secure_options(self, url: str) -> None:
		"""
		Method that applies the TLS and connection options shared by every request.
		"""
		curl = self._curl
		curl.setopt(curl.URL, url)
		curl.setopt(curl.SSL_VERIFYPEER, 1)
		curl.setopt(curl.SSL_VERIFYHOST, 2)
		curl.setopt(curl.SSLVERSION, curl.SSLVERSION_TLSv1_2)
		curl.setopt(curl.PROTOCOLS, curl.PROTO_HTTPS)
		curl.setopt(curl.FOLLOWLOCATION, 0)
		curl.setopt(curl.CONNECTTIMEOUT, self.CONNECT_TIMEOUT)


	def _retry_delay(self, http_code: int, attempt: int) -> float:
		"""
		Method that calculates how long to wait before retrying.
		Honors Telegram's `retry_after` on 429, otherwise uses exponential backoff.
		"""
		delay = float(2 ** attempt)
		if http_code == 429:
			try:
				retry_after = json.loads(self.last_response_body)["parameters"]["retry_after"]
				delay = float(retry_after)
			except (ValueError, KeyError, TypeError):
				pass
		return min(delay, self.MAX_RETRY_WAIT)


	def _build_url(self, token: str, method: str) -> str:
		return f"https://api.telegram.org/bot{token}/{method}"


	def _validate_token(self, token: str) -> None:
		if not isinstance(token, str) or not self._TOKEN_RE.match(token):
			raise ValueError("Invalid Telegram bot token format")


	def _validate_chat_id(self, chat_id: str) -> None:
		if not self._CHAT_ID_RE.match(str(chat_id)):
			raise ValueError("Invalid Telegram chat ID format")


	def _validate_file(self, file: str) -> Path:
		"""
		Method that validates the file to upload (existence, location and size).
		"""
		path = Path(file).resolve()
		if not path.is_file():
			raise FileNotFoundError(f"File not found: {file}")
		if self._allowed_dir is not None and not path.is_relative_to(self._allowed_dir):
			raise PermissionError("File is outside the allowed directory")
		if path.stat().st_size > self.MAX_FILE_SIZE:
			raise ValueError("File exceeds Telegram's 50 MB limit")
		return path

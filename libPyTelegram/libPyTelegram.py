"""
Author: Erick Roberto Rodriguez Rodriguez
Email: erodriguez@tekium.mx, erickrr.tbd93@gmail.com
GitHub: https://github.com/erickrr-bd/libPyTelegram
libPyTelegram v2.2 - March 2025
"""
from io import StringIO
from dataclasses import dataclass
from urllib.parse import urlencode
from pycurl import Curl, HTTP_CODE, FORM_FILE

@dataclass
class libPyTelegram:
	"""
	Easy sending messages via Telegram with Pycurl. 
	"""

	def send_telegram_message(self, telegram_bot_token: str, telegram_chat_id: str, telegram_message: str) -> int:
		"""
		Method that sends a text message via Telegram.

		Parameters:
			telegram_bot_token (str): Telegram Bot Token.
			telegram_chat_id (str): Telegram Chat ID.
			telegram_message (str): Message to send.

		Returns:
			telegram_message (int): HTTP code returned by the Telegram API.
		"""
		curl = Curl()
		url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
		curl.setopt(curl.URL, url)
		data = {"chat_id" : telegram_chat_id, "text" : telegram_message}
		post_fields = urlencode(data)
		curl.setopt(curl.POSTFIELDS, post_fields)
		curl.perform_rs()
		response_http_code = curl.getinfo(HTTP_CODE)
		curl.close()
		return response_http_code
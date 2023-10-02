from io import StringIO
from urllib.parse import urlencode
from pycurl import Curl, HTTP_CODE, FORM_FILE

class libPyTelegram:

	def sendMessageTelegram(self, telegram_bot_token, telegram_chat_id, telegram_message):
		"""
		Method that sends a text message via Telegram API.

		Returns the HTTP code of the response.

		:arg telegram_bot_token (string): Telegram Bot Token.
		:arg telegram_chat_id (string): Telegram channel identifier.
		:arg telegram_message (string): Message to send via Telegram.
		"""
		if len(telegram_message) > 4096:
			telegram_message = "The size of the message in Telegram (4096) has been exceeded. Overall size: " + str(len(telegram_message))
		c = Curl()
		url = "https://api.telegram.org/bot" + str(telegram_bot_token) + "/sendMessage"
		c.setopt(c.URL, url)
		data = {"chat_id" : telegram_chat_id, "text" : telegram_message}
		pf = urlencode(data)
		c.setopt(c.POSTFIELDS, pf)
		c.perform_rs()
		response_http_code = c.getinfo(HTTP_CODE)
		c.close()
		return response_http_code


	def sendFileMessageTelegram(self, telegram_bot_token, telegram_chat_id, telegram_message, file):
		"""
		Method that sends a message and an attached file using the Telegram API.

		Returns the HTTP code of the response.

		:arg telegram_bot_token (string): Telegram Bot Token.
		:arg telegram_chat_id (string): Telegram channel identifier.
		:arg telegram_message (string): Message to send via Telegram.
		:arg file (string): File to send via Telegram.
		"""
		url = "https://api.telegram.org/bot" + str(telegram_bot_token) + '/'
		data = [("chat_id", telegram_chat_id), ("document", (FORM_FILE, file))]
		data.append(("caption", telegram_message))
		c = Curl()
		storage = StringIO()
		c.setopt(c.URL, url + "sendDocument")
		c.setopt(c.HTTPPOST, data)
		c.perform_rs()
		response_http_code = c.getinfo(HTTP_CODE)
		c.close()
		return response_http_code
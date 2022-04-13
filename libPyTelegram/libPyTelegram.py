from io import StringIO
from urllib.parse import urlencode
from pycurl import Curl, HTTP_CODE, FORM_FILE

class libPyTelegram:

	def sendMessageTelegram(self, telegram_bot_token, telegram_chat_id, message_to_send):
		"""
		Method that sends a message using the Telegram API.

		:arg telegram_bot_token: Telegram bot token that will be used to send the messages.
		:arg telegram_chat_id: Identifier of the Telegram channel where the messages will be sent.
		:arg message_to_send: Message to send to the Telegram channel.
		"""
		if len(message_to_send) > 4096:
			message_to_send = "The size of the message in Telegram (4096) has been exceeded. Overall size: " + str(len(message_to_send))
		c = Curl()
		url = 'https://api.telegram.org/bot' + str(telegram_bot_token) + '/sendMessage'
		c.setopt(c.URL, url)
		data = {'chat_id' : telegram_chat_id, 'text' : message_to_send}
		pf = urlencode(data)
		c.setopt(c.POSTFIELDS, pf)
		c.perform_rs()
		status_code = c.getinfo(HTTP_CODE)
		c.close()
		return status_code


	def sendFileMessageTelegram(self, telegram_bot_token, telegram_chat_id, message_to_send, file_to_send):
		"""
		Method that sends a message and an attached file using the Telegram API.

		:arg telegram_bot_token: Telegram bot token that will be used to send the messages.
		:arg telegram_chat_id: Identifier of the Telegram channel where the messages will be sent.
		:arg message_to_send: Message to send to the Telegram channel.
		:arg file_to_send: File that will be sent attached to the message to the Telegram channel.
		"""
		url = 'https://api.telegram.org/bot' + str(telegram_bot_token) + '/'
		data = [("chat_id", telegram_chat_id), ('document', (FORM_FILE, file_to_send))]
		data.append(("caption", message_to_send))
		c = Curl()
		storage = StringIO()
		c.setopt(c.URL, url + 'sendDocument')
		c.setopt(c.HTTPPOST, data)
		c.perform_rs()
		status_code = c.getinfo(HTTP_CODE)
		c.close()
		return status_code
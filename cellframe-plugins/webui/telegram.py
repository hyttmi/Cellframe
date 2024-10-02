import urllib.parse
import urllib.request
from utils import getConfigValue, logError, logNotice

def sendTelegram(text):
    API_TOKEN = getConfigValue("webui", "telegram_api_key")
    CHAT_ID = getConfigValue("webui", "telegram_chat_id")
    try:
        if API_TOKEN is not None and CHAT_ID is not None:
            CHAT_ID= CHAT_ID[1:-1] # Remove "" for now, python-cellframe does not support uint64 yet.
            url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
            payload = {
                'chat_id': CHAT_ID,
                'text': text,
                'parse_mode': "HTML"
            }
            data = urllib.parse.urlencode(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                logNotice(f"Telegram response: {response_data}")
        else:
            logError("Missing configuration for Telegram messages, make sure that you have telegram_api_key and telegram_chat_id set!")
            return

    except urllib.error.HTTPError as e:
        logError(f"HTTP Error: {e.code}, Reason: {e.reason}")
        response = e.read().decode('utf-8')
        logError(f"Response from server: {response}")
    except Exception as e:
        logError(f"Error: {e}")
        return

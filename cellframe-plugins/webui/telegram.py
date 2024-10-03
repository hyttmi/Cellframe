import requests
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
            res = requests.get(url, params=payload)
            if res.status_code == requests.codes.ok:
                logNotice("Telegram message sent!")
            else:
                logError("Sending Telegram message failed!")
        else:
            logError("Missing configuration for Telegram messages, make sure that you have telegram_api_key and telegram_chat_id set!")
            return

        
    except Exception as e:
        logError(f"Error: {e}")
        return

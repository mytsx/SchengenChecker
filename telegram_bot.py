import requests
from config_loader import ConfigLoader, ConfigWrapper


class TelegramBot:

    def __init__(self, config_file="telegram.json"):
        """
        Telegram botunu başlatır.

        Args:
            token (str): BotFather'dan alınan bot API tokeni.
        """
        config_data = ConfigLoader.load_config(config_file)
        config = ConfigWrapper(config_data)

        self.token = config.get("telegram_token")
        self.chat_id = config.get("telegram_chat_id")
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text):
        """
        Telegram üzerinden mesaj gönderir.

        Args:
            chat_id (str): Kullanıcının chat_id'si.
            text (str): Gönderilecek mesaj.
        """
        url = f"{self.api_url}/sendMessage"
        data = {"chat_id": self.chat_id, "text": text}
        response = requests.post(url, data=data)
        return response.json()

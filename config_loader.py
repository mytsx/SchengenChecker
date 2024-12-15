import json
import os


class ConfigLoader:
    CONFIG_DIR = "config"  # Yapılandırma dosyalarının bulunduğu klasör

    @staticmethod
    def load_config(file_name):
        """
        Verilen dosya adını `config` klasöründen yükler ve içeriğini döndürür.

        Args:
            file_name (str): JSON dosyasının adı.

        Returns:
            dict: JSON dosyasının içeriği.

        Raises:
            FileNotFoundError: Dosya bulunamazsa.
            json.JSONDecodeError: JSON formatı geçerli değilse.
        """
        file_path = os.path.join(ConfigLoader.CONFIG_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Hata: {file_path} bulunamadı.")
            raise
        except json.JSONDecodeError as e:
            print(f"Hata: {file_path} JSON formatı geçerli değil. Detay: {e}")
            raise


class ConfigWrapper:

    def __init__(self, config_data):
        self.config_data = config_data

    def get(self, key, default=None):
        return self.config_data.get(key, default)

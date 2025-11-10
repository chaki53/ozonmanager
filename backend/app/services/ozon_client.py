# Заглушка клиента Ozon API
class OzonClient:
    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key
    def ping(self):
        return True

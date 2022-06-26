import requests, secrets
credentials = secrets.get_credentials()
url = "https://api.telegram.org/bot"
class TelegramBot():
    def __init__(self):
        self.api_key = credentials["TelegramAPIKey"]
        self.chat_id = credentials["TelegramChannel"]
        pass

    async def post(self, message):
        
        request = url + self.api_key + f"/sendMessage?chat_id={self.chat_id}&text={message}"
        result = requests.get(request).json()
        return result["result"]

    async def getMe(self):
        request = url+self.api_key+f"/getMe"
        print("getMeRequest:",request)
        result = requests.get(request).json()
        return result["result"]
        
    async def getUpdates(self):
        request= url+self.api_key+f"/getUpdates"
        result= requests.get(request).json()
        return result["result"]

    async def Login(self, browser):
        self.browser = browser
        
from requests import Response


class BaseProxySmartException(Exception):
    pass


class IncorrectResponseStatusCode(Exception):
    def __init__(self, message: str, response: Response):
        self.response = response
        self.message = message

    def __str__(self):
        return f"{self.message}\n" \
               f"IncorrectResponseStatusCode code: {self.response.status_code}, text: {self.response.text}"

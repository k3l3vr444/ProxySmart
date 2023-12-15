from pydantic import BaseModel, HttpUrl, StrictStr


class Server(BaseModel):
    url: HttpUrl
    login: StrictStr
    password: StrictStr

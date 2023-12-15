from pydantic import BaseModel, StrictStr, PositiveInt, HttpUrl


class Modem(BaseModel):
    imei: StrictStr
    http: PositiveInt
    socks5: PositiveInt
    nickname: StrictStr
    login: StrictStr
    password: StrictStr
    rotation_link: HttpUrl


class ModemBandwidth(BaseModel):
    imei: StrictStr
    in_: StrictStr
    out: StrictStr

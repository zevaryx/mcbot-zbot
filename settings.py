from mcbot.settings import Settings as BaseSettings

class Settings(BaseSettings):
    alert_for_multibyte: bool = False

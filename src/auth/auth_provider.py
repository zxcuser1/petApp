from authx import AuthX, AuthXConfig
import os

from dotenv import load_dotenv

load_dotenv()
config = AuthXConfig()

config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_ALGORITHM = os.getenv("JWT_ALG")
token_provider = AuthX(config=config)

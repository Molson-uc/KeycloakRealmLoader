from dotenv import load_dotenv
import os


class Config:
    def __init__(self) -> None:

        load_dotenv()
        self.realm = os.getenv("REALM", "master")
        self.host = os.getenv("HOST", "http://127.0.0.1:8080")
        self.admin_name = os.getenv("ADMIN_NAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin")

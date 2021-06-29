import json
import os
import pathlib
from typing import Optional, AnyStr

import requests


class AnoBbsClient:
    DEFAULT_CONFIG_PATH = pathlib.Path(f"{os.environ['HOME']}/.config/anobbs_cli/config.json")
    DEFAULT_CONFIG = {
        "addr": "http://host:port",
        "account_id": "",
    }

    class AnoBbsHttpApi:
        AppendPage = "/api/v1/append_page"
        GroupList = "/api/v1/group_list"
        CreateAccount = "/api/v1/create_account"
        Login = "/api/v1/login"
        PostPage = "/api/v1/post_page"
        QueryAccount = "/api/v1/query_account"
        QueryGroupWithPages = "/api/v1/query_group_with_pages"
        QueryPageWithFloors = "/api/v1/query_page_with_floors"

        @classmethod
        def add_addr(cls, addr: str):
            return [
                getattr(cls, addr + attr)
                for attr
                in dir(cls)
                if not attr.startswith("__") and attr != "add_addr"
            ]

    def __write_config(self):
        self.__get_config()
        with open(self.DEFAULT_CONFIG_PATH, "w") as file:
            file.write(json.dumps(self.config, indent=2))

    def __get_config(self) -> Optional[dict]:
        os.makedirs(self.DEFAULT_CONFIG_PATH.parent, exist_ok=True)
        if not self.DEFAULT_CONFIG_PATH.is_file():
            with open(self.DEFAULT_CONFIG_PATH, "w") as file:
                file.write(json.dumps(self.DEFAULT_CONFIG, indent=2))
            return None
        else:
            with open(self.DEFAULT_CONFIG_PATH, "r") as file:
                config = json.load(file)
            return config

    @staticmethod
    def __send_request(
            api: AnyStr,
            method: AnyStr,
            data: Optional[dict] = None,
    ):
        method = method.lower()
        if method == "post":
            res = requests.post(api, json=data)
        elif method == "get":
            res = requests.get(api)
        else:
            return None

        if res.status_code == 200:
            data = res.json()
            if data.get("code", 1) == 0:
                return data.get("data")
        return None

    @staticmethod
    def post(
            api: AnyStr,
            data: Optional[dict] = None,
    ):
        return AnoBbsClient.__send_request(api, "post", data)

    @staticmethod
    def get(api: AnyStr) -> Optional[dict]:
        return AnoBbsClient.__send_request(api, "get")

    def __init__(self):
        self.config = self.__get_config()
        if self.config is None:
            raise RuntimeError(f"Please edit config file: {self.DEFAULT_CONFIG_PATH}")
        else:
            self.AnoBbsHttpApi.add_addr(self.config["addr"])
        self.account_id = self.config.get("account_id")

    def create_account(self, ic: AnyStr) -> Optional[AnyStr]:
        res = self.post(self.AnoBbsHttpApi.CreateAccount, {"invitation_code": ic})
        if res:
            self.config["account_id"] = res
            self.__write_config()
            return res
        return None

    def login(self, account_id: AnyStr) -> Optional[AnyStr]:
        res = self.post(self.AnoBbsHttpApi.Login, {"account_id": account_id})
        if res:
            self.config["token"] = res
            self.__write_config()
            return res
        return None
        pass

__all__ = [
    "ano_bbs_client",
]

import json
import logging
import os
import pathlib
from typing import Optional, AnyStr, List

import requests

logger = logging.getLogger("AnoBbsClient")


class AnoBbsClient:
    class ConfigKeys:
        ADDR = "address"
        ACCOUNT = "account_id"
        TOKEN = "token"
        ANOCODES = "ano_codes"
        NOW_ANOCODE = "now_ano_code"
        UI_USE_LINE_BORDER = "use_line_border"

    DEFAULT_CONFIG_PATH = pathlib.Path(f"{os.environ['HOME']}/.config/anobbs_cli/config.json")
    DEFAULT_CONFIG = {
        ConfigKeys.ADDR: "http://host:port",
        ConfigKeys.ACCOUNT: "",
        ConfigKeys.TOKEN: "",
        ConfigKeys.ANOCODES: "",
        ConfigKeys.NOW_ANOCODE: "",
        ConfigKeys.UI_USE_LINE_BORDER: False,
    }

    class AnoBbsHttpApi:
        AppendPage = "/api/v1/append_page"
        BlockAnoCodeByFloorNo = "/api/v1/block_ano_code_by_floor_no"
        GroupList = "/api/v1/group_list"
        CreateAccount = "/api/v1/create_account"
        CreateAnoCode = "/api/v1/create_ano_code"
        CreateInvitationCode = "/api/v1/create_invitation_code"
        Login = "/api/v1/login"
        PostPage = "/api/v1/post_page"
        QueryAccount = "/api/v1/query_account"
        QueryAccountTree = "/api/v1/query_account_tree"
        QueryGroupWithPages = "/api/v1/query_group_with_pages"
        QueryPageWithFloors = "/api/v1/query_page_with_floors"
        HelloWorld = "/api/v1/hello_world"

        @classmethod
        def add_addr(cls, addr: str):
            return [
                setattr(cls, attr, addr + getattr(cls, attr))
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
                config = {
                    **self.DEFAULT_CONFIG,
                    **json.load(file)
                }
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
            else:
                logger.error(f"{api} {method.upper()} {data}")
        return None

    @staticmethod
    def _post(
            api: AnyStr,
            data: Optional[dict] = None,
    ):
        return AnoBbsClient.__send_request(api, "post", data)

    @staticmethod
    def _get(api: AnyStr) -> Optional[dict]:
        return AnoBbsClient.__send_request(api, "get")

    def __init__(self):
        self.config = self.__get_config()
        if self.config is None:
            raise RuntimeError(f"Please edit config file: {self.DEFAULT_CONFIG_PATH}")
        else:
            self.AnoBbsHttpApi.add_addr(self.config[self.ConfigKeys.ADDR])
        self.account_id = self.config.get(self.ConfigKeys.ACCOUNT)
        if not self.hello_world():
            raise RuntimeError(f"Server address error: {self.config[self.ConfigKeys.ADDR]}")

    def hello_world(self) -> bool:
        try:
            return self._get(self.AnoBbsHttpApi.HelloWorld) is not None
        except Exception as error:
            logger.error(error)
            return False

    def create_account(self, ic: AnyStr) -> Optional[AnyStr]:
        res = self._post(self.AnoBbsHttpApi.CreateAccount, {"invitation_code": ic})
        if res:
            self.config[self.ConfigKeys.ACCOUNT] = res
            self.login()
            self.__write_config()
            return res
        return None

    def create_ic(self) -> Optional[AnyStr]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None
        return self._post(self.AnoBbsHttpApi.CreateInvitationCode, {"token": token})

    def create_ac(self) -> Optional[AnyStr]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None
        res = self._post(self.AnoBbsHttpApi.CreateAnoCode, {"token": token})
        if res:
            self.query_account()
            return res
        return None

    def login(self) -> Optional[AnyStr]:
        res = self._post(self.AnoBbsHttpApi.Login, {
            "account_id": self.config.get(self.ConfigKeys.ACCOUNT)
        })
        if res:
            self.config[self.ConfigKeys.TOKEN] = res
            account = self.query_account()
            if account:
                ac_list = [
                    ac_obj.get("id")
                    for ac_obj
                    in account.get("ac_list", [])
                    if not ac_obj.get("is_blocked")
                ]
                self.config[self.ConfigKeys.ANOCODES] = ac_list
                if len(ac_list) > 0:
                    default_anocode = ac_list[0]
                    self.config[self.ConfigKeys.NOW_ANOCODE] = default_anocode
                    logger.info(
                        f"You can select default anocode in {self.DEFAULT_CONFIG_PATH}\n"
                        f"Now anocode: {default_anocode}"
                    )
            self.__write_config()
            return res
        return None

    def list_group(self) -> Optional[List[AnyStr]]:
        return self._get(self.AnoBbsHttpApi.GroupList)

    def append_page(self, page_id: AnyStr, content: AnyStr) -> Optional[dict]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None

        ac = self.config.get(self.ConfigKeys.NOW_ANOCODE)
        if not ac:
            return None

        return self._post(self.AnoBbsHttpApi.AppendPage, {
            "page_id": page_id,
            "token": token,
            "ano_code": ac,
            "content": content,
        })

    def post_page(self, content: AnyStr, group_name: AnyStr = "all") -> Optional[dict]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None
        ac = self.config.get(self.ConfigKeys.NOW_ANOCODE)
        if not ac:
            return None

        return self._post(self.AnoBbsHttpApi.PostPage, {
            "token": token,
            "ano_code": ac,
            "content": content,
            "group_name": group_name,
        })

    def query_group_with_pages(
            self,
            group_name: AnyStr = "all",
            page_size: int = 30,
            page_index: int = 1,
    ) -> Optional[dict]:
        return self._post(self.AnoBbsHttpApi.QueryGroupWithPages, {
            "group_name": group_name,
            "page_size": page_size,
            "page_index": page_index,
        })

    def query_page_with_floor(
            self,
            page_id: AnyStr,
            page_size: int = 50,
            page_index: int = 1,
    ) -> Optional[dict]:
        return self._post(self.AnoBbsHttpApi.QueryPageWithFloors, {
            "page_id": page_id,
            "page_size": page_size,
            "page_index": page_index,
        })

    def query_account(self) -> Optional[dict]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None
        return self._post(self.AnoBbsHttpApi.QueryAccount, {
            "token": token,
        })

    def query_account_tree(self) -> Optional[AnyStr]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None

        return self._post(self.AnoBbsHttpApi.QueryAccountTree, {
            "token": token,
        })

    def block_ac_by_floor_no(self, floor_no: AnyStr) -> Optional[AnyStr]:
        token = self.config.get(self.ConfigKeys.TOKEN)
        if not token:
            return None
        return self._post(self.AnoBbsHttpApi.BlockAnoCodeByFloorNo, {"token": token, "floor_no": floor_no})


try:
    ano_bbs_client = AnoBbsClient()
except RuntimeError as err:
    logging.error(err)
    exit(1)

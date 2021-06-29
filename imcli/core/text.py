from typing import AnyStr

from .base_ui_object import BaseUiObject


class Text(BaseUiObject):
    def __init__(self, content: AnyStr):
        super().__init__(content)

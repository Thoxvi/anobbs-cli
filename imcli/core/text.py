from typing import AnyStr

from imcli.core.base_ui_object import BaseUiObject


class Text(BaseUiObject):
    @classmethod
    def chunks_str(cls, lst, n) -> AnyStr:
        lines = []
        for i in range(0, len(lst), n):
            lines.append(lst[i:i + n])
        return "\n".join(lines)

    def __init__(self, content: AnyStr, max_lenght: int = 32, **kwargs):
        super().__init__(**kwargs)
        self._max_lenght = max_lenght
        self.set_content(content)

    def set_content(self, content: AnyStr) -> bool:
        self._content = self.chunks_str(content, self._max_lenght)
        return True


if __name__ == '__main__':
    t = Text("123456", 6)
    print(t.render())
    t = Text("123456", 6, use_line_border=False)
    print(t.render())

from typing import AnyStr

from imcli.core.base_ui_object import BaseUiObject


class Text(BaseUiObject):
    @classmethod
    def chunks_str(cls, lst, n) -> AnyStr:
        lines = []
        if n < 0:
            return lst
        for i in range(0, len(lst), n):
            lines.append(lst[i:i + n])
        return "\n".join(lines)

    def __init__(self, content: AnyStr, max_lenght=32, min_lenght: int = 32, **kwargs):
        super().__init__(**kwargs)
        self._min_lenght = min(min_lenght, max_lenght)
        self._max_lenght = max(max_lenght, min_lenght)
        self.set_content(content)

    def set_content(self, content: AnyStr) -> bool:
        content = content.replace("\t", " " * 4)

        self._content = "\n".join(
            line + " " * max(0, self._min_lenght - len(line))
            for line
            in [
                self.chunks_str(content, self._max_lenght)
                for content
                in content.split("\n")
            ])
        return True


if __name__ == '__main__':
    t = Text("12\n3456", 6, use_line_border=False)
    print(t.render())
    t = Text("123\n456", 6)
    print(t.render())
    t = Text("123\n456", 6, 10)
    print(t.render())

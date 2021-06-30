__all__ = [
    "BaseUiObject"
]

from typing import AnyStr


class BaseUiObject:
    @classmethod
    def add_line_border(cls, content: AnyStr) -> str:
        content_matrix = content.split("\n")
        max_x = max([len(line) for line in content_matrix])
        output = ["┌" + max_x * "─" + "┐"]
        for line in content_matrix:
            output.append("│" + line + "│")
        output.append("└" + max_x * "─" + "┘")

        return "\n".join(output)

    @classmethod
    def add_blank_border(cls, content: AnyStr, border_size: int = 0) -> str:
        content_matrix = content.split("\n")
        output = []
        for line in content_matrix:
            output.append(" " * border_size + line + " " * border_size)
        return "\n".join(output)

    @classmethod
    def render_to_rectangle(cls, content: AnyStr) -> AnyStr:
        content_matrix = content.split("\n")
        max_x = max([len(line) for line in content_matrix])
        content_matrix = [
            line + " " * (max_x - len(line))
            for line
            in content_matrix
        ]
        return "\n".join(content_matrix)

    def __init__(
            self, content: AnyStr = "",
            lr_margin: int = 1,
            lr_padding: int = 1,
            use_line_border: bool = True
    ):
        self._content = content.replace("\t", " " * 4)
        self._lr_margin = lr_margin
        self._lr_padding = lr_padding
        self._use_line_border = use_line_border

    def render(self) -> AnyStr:
        content = self.render_to_rectangle(self._content)
        content = self.add_blank_border(content, self._lr_margin)
        if self._use_line_border:
            content = self.add_line_border(content)
        content = self.add_blank_border(content, self._lr_padding)
        return content

    def __str__(self):
        return self.render()


if __name__ == '__main__':
    bio = BaseUiObject("""hhhhhhhhhhhhh1
hhhhhhhhhhhh2
h3""")
    print(bio.render())

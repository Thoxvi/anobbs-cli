__all__ = [
    "HorizontalLayout",
    "VerticalLayout",
]

from typing import List, AnyStr

from imcli.core.base_ui_object import BaseUiObject


class Layout(BaseUiObject):
    def __init__(self, sub_ui_list: List[BaseUiObject] = None, **kwargs):
        super().__init__(**kwargs)
        self._sub_ui_list: List[BaseUiObject] = sub_ui_list if sub_ui_list else []

    def add_ui(self, ui: BaseUiObject) -> None:
        self._sub_ui_list.append(ui)


class VerticalLayout(Layout):
    def __init__(self, sub_ui_list: List[BaseUiObject] = None, **kwargs):
        super().__init__(sub_ui_list, **kwargs)

    def render(self) -> AnyStr:
        return "\n".join(
            ui.render()
            for ui
            in self._sub_ui_list
        )


class HorizontalLayout(Layout):
    def __init__(self, sub_ui_list: List[BaseUiObject] = None, **kwargs):
        super().__init__(sub_ui_list, **kwargs)

    def render(self) -> AnyStr:
        sub_ui_matrix = [
            ui.render()
            for ui
            in self._sub_ui_list
        ]
        max_y = max([
            len(ui.split("\n"))
            for ui
            in sub_ui_matrix
        ])
        sub_ui_splited_matrix = [
            ui_matrix.split("\n")
            for ui_matrix
            in sub_ui_matrix
        ]
        sub_ui_x_list = [
            len(ui_splited_matrix[0])
            for ui_splited_matrix
            in sub_ui_splited_matrix
        ]
        output = []
        for y in range(max_y):
            line = ""
            for x, ui_splited in enumerate(sub_ui_splited_matrix):
                if len(ui_splited) > y:
                    line += ui_splited[y]
                else:
                    line += " " * sub_ui_x_list[x]
            output.append(line)
        return "\n".join(output)


if __name__ == '__main__':
    vl = VerticalLayout([
        BaseUiObject("1\n2"),
        BaseUiObject("12"),
        BaseUiObject("123")
    ])
    print(vl.render())

    hl = HorizontalLayout([
        BaseUiObject("1\n2"),
        BaseUiObject("12"),
        BaseUiObject("123")
    ])
    print(hl.render())

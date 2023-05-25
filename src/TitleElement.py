from mesa.visualization.modules import TextElement


class TitleElement(TextElement):
    def __init__(
        self, text: str = "", center: bool = True, padding_left: int = 0
    ) -> None:
        self.text = text
        self.center = center
        self.padding_left = padding_left

    def render(self, model) -> str:
        if self.center:
            return f'<h2 style="padding-top: 15px; text-align: center; padding-left: {self.padding_left}px;">{self.text}</h2>'
        else:
            return f'<h2 style="padding-top: 10px; padding-left: {self.padding_left}px;">{self.text}</h2>'

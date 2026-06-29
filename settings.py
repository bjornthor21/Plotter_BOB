from dataclasses import dataclass

@dataclass
class Settings:
    feed: int = 1000
    draw_text: bool = True
    draw_mtext: bool = True
    draw_dimensions: bool = True
    draw_border: bool = True
    draw_title_block: bool = True
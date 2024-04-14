from PIL import ImageFont
from typing import Tuple, Optional

import pkg_resources

expect_height: int = 1500
"""期望图像高度"""
bg_color: Tuple[int, int, int] = (16, 16, 16)
"""背景颜色"""

# 分割设置
slice_height: int = 4800 + 24
"""
分割轨道的长度

这里最好是 `PPS` 的倍数 ± `NOTE_SIZE[2]`，否则note很有可能被切开
"""
x_sep: int = 80
"""轨道旁的留空宽度"""
frame_width: int = 16
"""轨道边框宽度"""
sep_line_width: int = 4
"""轨道分割线宽度"""
lane_width: int = 50
"""轨道间距"""
lane_range: Tuple[Optional[int], Optional[int]] = (None, None)
"""
轨道范围

为 `(None, None)` 时将自动计算谱面轨道范围
"""
lane_num: Optional[int] = None
"""
轨道数

为 `None` 时将自动计算谱面轨道数
"""

# 字体设置
font_file: str = ""
"""绘制BPM和时长的字体"""

_font: Optional[ImageFont.FreeTypeFont] = None
def font() -> ImageFont.FreeTypeFont:
    global _font
    if _font is None:
        if font_file == "":
            _file = pkg_resources.resource_filename(__name__, "resources/fonts/TT-Shin Go M.ttf")
            _font = ImageFont.truetype(_file, 24)
        else:
            _font = ImageFont.truetype(font_file, 24)
    return _font

# 颜色设置
frame_color: Tuple[int, int, int, int] = (0, 77, 77, 255)
"""轨道边框颜色"""
sep_line_color: Tuple[int, int, int, int] = (19, 119, 151, 50)
"""轨道分割线颜色"""
double_beat_line_color: Tuple[int, int, int] = (220, 220, 220)
"""双押线颜色"""
bpm_line_light_color: Tuple[int, int, int, int] = (255, 51, 119, 224)
"""醒目小节线颜色（更换BPM后第一条小节线）"""
bpm_line_color: Tuple[int, int, int, int] = (240, 240, 240, 100)
"""小节线颜色"""
bpm_text_color: Tuple[int, int, int] = (255, 51, 119)
"""绘制BPM的颜色"""
time_text_color: Tuple[int, int, int] = (255, 255, 255)
"""绘制时长的颜色"""
note_num_color: Tuple[int, int, int] = (255, 255, 255)
"""绘制物量的颜色"""

# 其他设置
color_light_value: int = 60
"""颜色亮度升高数值"""
x_offset: int = 4
"""note的左右偏移量"""
pps: int = 480
"""每秒像素数"""
skin: str = "skin00_rip"
"""皮肤"""
blue_white_tap: bool = True
"""
蓝白键节奏色觉辅助

- `True`: 开启
- `False`: 关闭
"""
flick_offset: int = 9
"""滑键上下偏移量"""
directional_offset: int = 4
"""方向键左右偏移量"""
directional_arrow_offset: int = -6
"""方向键箭头左右偏移量"""
note_size: Tuple[int, int] = (60, 24)
"""note的大小"""
double_beat_line_width: int = 2
"""双押线的宽度"""
bpm_line_width: int = 2
"""小节线的宽度"""

# BanGDreamChartRender

_⭐  使用 Python 编写的 BanGDream 谱面渲染工具  ⭐_


## 功能性
BanGDreamChartRender 支持负BPM，几乎所有轨道数量，SP绿条绘制，节奏的色觉辅助等众多功能

## 配置
| 参数名 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| EXPECT_HEIGHT | int | 1500 | 期望图像高度 |
| BG_COLOR | tuple | (16, 16, 16) | 背景颜色 |
| SLICE_HEIGHT | int | 3360 + 24 | 分割轨道的长度，这里最好是 `PPS` 的倍数 ± `NOTE_SIZE[2]`，否则note很有可能被切开 |
| X_SEP | int | 80 | 轨道旁的留空宽度 |
| FRAME_WIDTH | int | 16 | 轨道边框宽度 |
| SEP_LINE_WIDTH | int | 4 | 轨道分割线宽度 |
| LANE_WIDTH | int | 50 | 轨道间距 |
| LANE_RANGE | tuple | (None, None) | 轨道范围，为`(None, None)`时将自动计算谱面轨道范围 |
| LANE_NUM | int | None | 轨道数，为`None`时将自动计算谱面轨道数 |
| FONT | ImageFont.ImageFont | ImageFont.truetype("fonts/TT-Shin Go M.ttf", size=24) | 绘制BPM、时长和物量的字体 |
| FRAME_COLOR | tuple | (0, 77, 77, 255) | 轨道边框颜色 |
| SEP_LINE_COLOR | tuple | (19, 119, 151, 50) | 轨道分割线颜色 |
| DOUBLE_BEAT_LINE_COLOR | tuple | (220, 220, 220) | 双押线的颜色 |
| BPM_LINE_LIGHT_COLOR | tuple | (255, 51, 119, 224) | 醒目小节线颜色（更换BPM后第一条小节线） |
| BPM_LINE_COLOR | tuple | (240, 240, 240, 100) | 小节线颜色 |
| BPM_TEXT_COLOR | tuple | (255, 51, 119) | 绘制BPM的颜色 |
| TIME_TEXT_COLOR | tuple | (255, 255, 255) | 绘制时长的颜色 |
| NOTE_NUM_COLOR | tuple | (255, 255, 255) | 绘制物量的颜色 |
| COLOR_LIGHT_VALUE | int | 60 | 颜色亮度升高数值 |
| X_OFFSET | int | 4 | note偏移量 |
| PPS | int | 480 | Pixel per Second |
| SKIN | str | "skin00_rip" | 皮肤 |
| BLUE_WHITE_TAP | bool | True | 蓝白键（节奏的色觉辅助） |
| FLICK_OFFSET | int | 9 | 滑键上下偏移量 |
| DIRECTIONAL_OFFSET | int | 4 | 方向键左右偏移量 |
| DIRECTIONAL_ARROW_OFFSET | int | -6 | 方向键的箭头左右偏移量 |
| NOTE_SIZE | tuple | (60, 24) | note的大小 |
| DOUBLE_BEAT_LINE_WIDTH | int | 2 |双押线的宽度 |
| BPM_LINE_WIDTH | int | 2 | 小节线厚度 |

## 使用
```python
import requests
from BanGDreamChartRender import render

url = "https://bestdori.com/api/post/details?id=101566"
response = requests.get(url)
data = response.json()

chart_img = render(data["post"]["chart"])
# `chart_img` 为 `PIL.Image.Image`
chart_img.show()
chart_img.save("101566")
```

## 皮肤
项目中只有一套 `skin00_rip` 的皮肤，如要使用其他皮肤，可以在 [Bestdori](https://bestdori.com/)下载后使用 [Tools for Cutting Unity Sprites](https://github.com/zhanbao2000/unity_sprites_cut) 切割后重命名，放入 resources 文件夹下并更改 `SKIN` 的值为文件夹名

## 感谢
[Bestdori](https://bestdori.com/) : BanG Dream 最大的第三方网站  
[Tools for Cutting Unity Sprites](https://github.com/zhanbao2000/unity_sprites_cut) : 虽然我不是用这个项目切的，但是看着挺好用的（）

感谢灵喵, WindowsSov8, kumoSleeping在负BPM问题上的思路和启发
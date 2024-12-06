# Bestdori-Render

_⭐ Bestdori chart rendering tool written in Python ⭐_

[English](README.md) | [中文](README_zh.md)

## Features
Supports negative BPM, almost any number of lanes, SP green bar rendering, rhythm color vision assistance, and many other features.

## Configuration
| Parameter Name | Type | Default Value | Description |
| --- | --- | --- | --- |
| EXPECT_HEIGHT | int | 1500 | Expected image height |
| BG_COLOR | tuple | (16, 16, 16) | Background color |
| SLICE_HEIGHT | int | 3360 + 24 | Length of the split track, it is best to be a multiple of `PPS` ± `NOTE_SIZE[2]`, otherwise the note is likely to be cut |
| X_SEP | int | 80 | Width of the empty space next to the track |
| FRAME_WIDTH | int | 16 | Track border width |
| SEP_LINE_WIDTH | int | 4 | Track separation line width |
| LANE_WIDTH | int | 50 | Track spacing |
| LANE_RANGE | tuple | (None, None) | Track range, when `(None, None)` the track range will be automatically calculated |
| LANE_NUM | int | None | Number of tracks, when `None` the number of tracks will be automatically calculated |
| FONT | ImageFont.ImageFont | ImageFont.truetype("fonts/TT-Shin Go M.ttf", size=24) | Font for drawing BPM, duration, and note count |
| FRAME_COLOR | tuple | (0, 77, 77, 255) | Track border color |
| SEP_LINE_COLOR | tuple | (19, 119, 151, 50) | Track separation line color |
| DOUBLE_BEAT_LINE_COLOR | tuple | (220, 220, 220) | Double beat line color |
| BPM_LINE_LIGHT_COLOR | tuple | (255, 51, 119, 224) | Highlighted measure line color (first measure line after BPM change) |
| BPM_LINE_COLOR | tuple | (240, 240, 240, 100) | Measure line color |
| BPM_TEXT_COLOR | tuple | (255, 51, 119) | Color for drawing BPM |
| TIME_TEXT_COLOR | tuple | (255, 255, 255) | Color for drawing duration |
| NOTE_NUM_COLOR | tuple | (255, 255, 255) | Color for drawing note count |
| COLOR_LIGHT_VALUE | int | 60 | Color brightness increase value |
| X_OFFSET | int | 4 | Note offset |
| PPS | int | 480 | Pixel per Second |
| SKIN | str | "skin00_rip" | Skin |
| BLUE_WHITE_TAP | bool | True | Blue-white key (rhythm color vision assistance) |
| FLICK_OFFSET | int | 9 | Flick note vertical offset |
| DIRECTIONAL_OFFSET | int | 4 | Directional note horizontal offset |
| DIRECTIONAL_ARROW_OFFSET | int | -6 | Directional note arrow horizontal offset |
| NOTE_SIZE | tuple | (60, 24) | Note size |
| DOUBLE_BEAT_LINE_WIDTH | int | 2 | Double beat line width |
| BPM_LINE_WIDTH | int | 2 | Measure line thickness |

## Usage
```python
import requests
from bestdori.render import render

url = "https://bestdori.com/api/post/details?id=101566"
response = requests.get(url)
data = response.json()

chart_img = render(data["post"]["chart"])
# `chart_img` is a `PIL.Image.Image`
chart_img.show()
chart_img.save("101566.png")
```

## Skins
The project only includes one set of `skin00_rip` skins. If you want to use other skins, you can download them from [Bestdori](https://bestdori.com/), use [Tools for Cutting Unity Sprites](https://github.com/zhanbao2000/unity_sprites_cut) to cut them, rename them, place them in the resources folder, and change the value of `SKIN` to the folder name.

## Acknowledgements
[Bestdori](https://bestdori.com/): The largest third-party website for BanG Dream  
[Tools for Cutting Unity Sprites](https://github.com/zhanbao2000/unity_sprites_cut): Although I didn't use this project to cut, it looks quite useful

Thanks to LingMiao, WindowsSov8, and kumoSleeping for their ideas and inspiration on the negative BPM issue.

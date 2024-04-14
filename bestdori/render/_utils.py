import pkg_resources
from pathlib import Path
from fractions import Fraction
from PIL import Image, ImageDraw
from typing import Any, Tuple, Optional, TypeAlias

from . import config

def _file(file_path: str) -> str:
    return pkg_resources.resource_filename(__name__, file_path)


_NoteType: TypeAlias = dict[str, Any]
_ChartType: TypeAlias = list[_NoteType]

class _Skins:
    def __init__(self) -> None:
        flick = Image.open(_file(f"resources/skins/{config.skin}/flick.png"))
        left = Image.open(_file(f"resources/skins/{config.skin}/left.png"))
        right = Image.open(_file(f"resources/skins/{config.skin}/right.png"))
        left_arrow = Image.open(_file(f"resources/skins/{config.skin}/left_arrow.png"))
        right_arrow = Image.open(_file(f"resources/skins/{config.skin}/right_arrow.png"))
        self.skin = {
            'flick' : flick.convert("RGBA").resize((config.note_size[0], int(flick.height / flick.width * config.note_size[0])), Image.Resampling.BICUBIC),
            'tap' : Image.open(_file(f"resources/skins/{config.skin}/tap.png")).convert("RGBA").resize(config.note_size, Image.Resampling.BICUBIC),
            'tap_white' : Image.open(_file(f"resources/skins/{config.skin}/tap_white.png")).convert("RGBA").resize(config.note_size, Image.Resampling.BICUBIC),
            'tap_skill' : Image.open(_file(f"resources/skins/{config.skin}/tap_skill.png")).convert("RGBA").resize(config.note_size, Image.Resampling.BICUBIC),
            'slide' : Image.open(_file(f"resources/skins/{config.skin}/slide.png")).convert("RGBA").resize(config.note_size, Image.Resampling.BICUBIC),
            'sep': Image.open(_file(f"resources/skins/{config.skin}/sep.png")).convert("RGBA").resize(config.note_size, Image.Resampling.BICUBIC),
            'long': Image.open(_file(f"resources/skins/{config.skin}/long.png")).convert("RGBA").resize((config.note_size[0], 1), Image.Resampling.BICUBIC),
            'left': left.convert("RGBA").resize((config.note_size[0], int(left.height / left.width * config.note_size[0])), Image.Resampling.BICUBIC),
            'right': right.convert("RGBA").resize((config.note_size[0], int(right.height / right.width * config.note_size[0])), Image.Resampling.BICUBIC),
            'left_arrow': left_arrow.convert("RGBA").resize((int(left_arrow.width / left_arrow.height * (left.height / left.width * config.note_size[0])), int(left.height / left.width * config.note_size[0])), Image.Resampling.BICUBIC),
            'right_arrow': right_arrow.convert("RGBA").resize((int(right_arrow.width / right_arrow.height * (right.height / right.width * config.note_size[0])), int(right.height / right.width * config.note_size[0])), Image.Resampling.BICUBIC),
        }

_skins: Optional[_Skins] = None

def skins() -> _Skins:
    global _skins
    if _skins is None:
        _skins = _Skins()
    return _skins

def get_second(bpm: float, beats: float) -> float:
    '''获取指定BPM的秒数'''
    return beats * (60 / bpm)

def _get_lighter_color(color: tuple) -> tuple:
    '''获取更亮的颜色'''
    if len(color) == 3:
        r, g, b = color
    else:
        r, g, b, a = color
        
    if max([r, g, b]) + config.color_light_value > 255:
        config.color_light_value = 255 - max([r, g, b])
    
    if len(color) == 3:
        return (r + config.color_light_value, g + config.color_light_value, b + config.color_light_value)
    return (r + config.color_light_value, g + config.color_light_value, b + config.color_light_value, a)

def get_lanes(height: int, chart: _ChartType) -> Tuple[Image.Image, Tuple[Optional[int], Optional[int]]]:
    '''获取轨道长图'''
    def _round(num):
        # 舍5进6
        if num >= 0:
            return int(num + 0.499999)
        else:
            return int(num - 0.499999)

    if config.lane_num is None or config.lane_range is None:
        # 计算轨道范围和数量
        simplified_chart = []
        for data in chart: # 将slide提到data层次，方便计算，同时忽略所有超过 -2 轨和 9 轨的音符
            if data['type'] == "Single" or data["type"] == "Directional":
                if data["lane"] < -2 or data["lane"] > 8:
                    continue
                
                simplified_chart.append(data)

            elif data["type"] == "Slide":
                for data_c in data["connections"]:
                    if data_c["lane"] < -2 or data_c["lane"] > 8:
                        continue
                    
                    simplified_chart.append({
                        "beat": data_c["beat"],
                        "lane": data_c["lane"],
                        "type": data["type"],
                        "pixel": data_c["pixel"]
                    })

        lanes = [data["lane"] for data in simplified_chart]
        lane_range = (_round(min(lanes)), _round(max(lanes)))
        lane_num = lane_range[1] - lane_range[0] + 1
    else:
        lane_range = config.lane_range
        lane_num = config.lane_num

    # 轨道数不能少于7
    if lane_num < 7:
        lane_num = 7
    
    width = config.frame_width * 2 + config.lane_width * lane_num
    lanes = Image.new("RGBA", (width + config.x_sep * 2, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(lanes)

    # 绘制左frame
    draw.rectangle((config.x_sep, 0, config.frame_width + config.x_sep, height), fill=config.frame_color)
    draw.rectangle((config.frame_width // 2 + config.x_sep, 0, config.frame_width + config.x_sep, height), fill=_get_lighter_color(config.frame_color))
    # 右frame
    draw.rectangle((width - config.frame_width + config.x_sep, 0, width + config.x_sep, height), fill=config.frame_color)
    draw.rectangle((width - config.frame_width + config.x_sep, 0, width - config.frame_width // 2 + config.x_sep, height), fill=_get_lighter_color(config.frame_color))

    # 绘制轨道分隔线
    x = config.frame_width - config.sep_line_width // 2
    for _ in range(0, lane_num + 1):
        draw.rectangle((x + config.x_sep, 0, x + config.sep_line_width + config.x_sep, height), config.sep_line_color)
        x += config.lane_width

    return lanes, lane_range

def get_bpm_timepoints(chart: _ChartType):
    '''获取谱面中所有BPM的timepoint'''
    # 感谢灵喵
    timepoints: _ChartType = list(filter(lambda n: n['type'] == 'BPM', chart)) # 筛选出类型为BPM的数据
    timepoints = sorted(timepoints, key=lambda x: x.get("beat", float('inf'))) # 按beat排序

    for i, data in enumerate(timepoints):
        if i == 0:
            timepoints[i]['time'] = 0
        else:
            timepoints[i]['time'] = timepoints[i - 1]['time'] + (data['beat'] - timepoints[i - 1]['beat']) * (60 / timepoints[i - 1]['bpm'])
    
    return timepoints

def get_timepoint_base(beat, timepoints):
    '''获取指定beat的前一个timepoint'''
    last_bpm = timepoints[0]
    for tp in timepoints:
        if tp['beat'] > beat:
            break
        last_bpm = tp
    return last_bpm

def get_note_time(beat, timepoints):
    '''获取note的绝对时间'''
    timepoint = get_timepoint_base(beat, timepoints)
    return timepoint["time"] + (beat - timepoint["beat"]) * (60 / timepoint["bpm"])

def preprocess_chart(chart: _ChartType) -> _ChartType:
    '''预处理谱面'''
    for data in chart:
        # long 和 slide 在视觉上无异，这里处理成 slide
        if data["type"] == "Long":
            data["type"] = "Slide"

    timepoints = get_bpm_timepoints(chart)
    # BPM 更换时间
    
    for idx, data in enumerate(chart):
        # 计算时间和y坐标
        note_type = data["type"]
        
        if note_type == "BPM" or note_type == "Single" or note_type == "Directional":
            chart[idx]["time"] = get_note_time(data["beat"], timepoints)
            chart[idx]["pixel"] = int(chart[idx]["time"] * config.pps)

        elif note_type == "Slide":
            for idx_c, data_c in enumerate(data["connections"]):
                chart[idx]["connections"][idx_c]["time"] = get_note_time(data_c["beat"], timepoints)
                chart[idx]["connections"][idx_c]["pixel"] = int(chart[idx]["connections"][idx_c]["time"] * config.pps)
    
    return chart

def corrent_chart(chart: _ChartType, lane_range: Tuple[Optional[int], Optional[int]]):
    '''将负轨修正'''
    if lane_range[0] is None or lane_range[0] >= 0:
        # 没有负轨，不需修正
        return chart

    lane_offset = -lane_range[0] # 轨道偏移数

    for idx, data in enumerate(chart):
        note_type = data["type"]

        if note_type == "Single" or note_type == "Directional":
            if data["lane"] < -2 or data["lane"] > 8: # 忽略掉超范围音符
                continue
            
            chart[idx]["lane"] += lane_offset
        
        elif note_type == "Slide":
            for idx_c in range(len(data["connections"])):
                if data["connections"][idx_c]["lane"] < -2 or data["connections"][idx_c]["lane"] > 8: # 忽略掉超范围音符
                    continue
            
                chart[idx]["connections"][idx_c]["lane"] += lane_offset
    return chart

def simplify_chart(chart: _ChartType) -> _ChartType:
    '''简化谱面，只保留tap, flick, directional, slide，用于计算双压'''
    simplified_chart = []
    for data in chart:
        if data["type"] == "Single" or data["type"] == "Directional":
            simplified_chart.append(data.copy())

        elif data["type"] == "Slide":
            for idx_c, data_c in enumerate(data["connections"]):
                if idx_c == 0 or idx_c == len(data["connections"]) - 1:
                    if not data_c.get("hidden", False):
                        simplified_chart.append({
                            "beat": data_c["beat"],
                            "lane": data_c["lane"],
                            "type": data["type"],
                            "pixel": data_c["pixel"]
                        })
    return simplified_chart

def _get_tapable_notes_data(chart: _ChartType) -> _ChartType:
    '''获取计入物量的note数据，用于绘制物量'''
    simplified_chart = []
    for data in chart:
        if data["type"] == "Single" or data["type"] == "Directional":
            simplified_chart.append(data)

        elif data["type"] == "Slide":
            for data_c in data["connections"]:
                if not data_c.get("hidden", False):
                    simplified_chart.append({
                        "beat": data_c["beat"],
                        "lane": data_c["lane"],
                        "type": data["type"],
                        "pixel": data_c["pixel"]
                    })
    return simplified_chart

def _fix_beats_data(chart: _ChartType) -> _ChartType:
    '''修正负 BPM 带来的 Beat 错误'''
    plain_chart: _ChartType = []
    for note in chart:
        if note['type'] == 'Slide':
            for index, connection in enumerate(note['connections']):
                if index == 0 or index == len(note['connections']) - 1:
                    _type = 'Slide'
                else:
                    _type = 'Connection'
                if not connection.get('hidden', False):
                    plain_chart.append({
                        'beat': connection['beat'],
                        'lane': connection['lane'],
                        'type': _type,
                        'pixel': connection['pixel']
                    })
        
        else:
            plain_chart.append(note.copy())
    
    plain_chart = sorted(plain_chart, key=lambda x: x.get('beat', float('inf')))
    
    negative = False
    last_beat = 0
    real_beat = 0
    result: _ChartType = []
    for index, note in enumerate(plain_chart):
        _beat: float = note.get('beat', 0)
        if negative:
            real_beat -= (_beat - last_beat)
        else:
            real_beat += (_beat - last_beat)
        last_beat = _beat
        note['beat'] = real_beat
        if note['type'] == 'BPM':
            if note.get('bpm', 0) < 0:
                negative = True
            else:
                negative = False
        else:
            result.append(note.copy())
    
    result = sorted(result, key=lambda x: x.get('beat', float('inf')), reverse=True)
    return result

def get_height(preprocessed_chart: _ChartType) -> int:
    '''获取谱面图片高度'''
    beat_line: list[Optional[float]] = [d.get("beat") for d in preprocessed_chart if isinstance(d.get("beat", None), (int, float))]
    beat_line += [c.get("beat") for d in preprocessed_chart for c in d.get("connections", []) if isinstance(c.get("beat"), (int, float))]
    max_beat = max(beat for beat in beat_line if beat is not None)

    data = next((d for d in preprocessed_chart if d.get("beat") == max_beat or any(c.get("beat") == max_beat for c in d.get("connections", []))), None)
    if data is None:
        raise ValueError("Failed to get the last note.")
    # 最后一个note

    if data["type"] == "BPM" or data["type"] == "Single" or data["type"] == "Directional":
        min_height = data["pixel"] + skins().skin["tap"].height
    else:
        min_height = data["connections"][-1]["pixel"] + skins().skin["tap"].height

    return int((min_height // config.slice_height + 1) * config.slice_height)

def get_bpm_data(chart: _ChartType) -> list[dict[str, Any]]:
    '''获取BPM数据，用于绘制BPM文本'''
    bpm_data = []
    for note in chart:
        if note["type"] == "BPM":
            bpm_data.append({
                "bpm": note["bpm"],
                "pixel": note["pixel"],
                "beat": note["beat"]
            })
    return bpm_data

def get_beat_data(chart: _ChartType) -> list[dict[str, Any]]:
    '''获取节奏间隔数据，用于绘制节奏间隔文本'''
    beat_data = []
    
    # 将谱面按照 beat 排序
    _chart = _fix_beats_data(chart)
    
    beat_now = 0.0
    _beat = 0.0
    type_now = ''
    index_now = 0
    for note in _chart:
        if (beat := note.get('beat', None)) is not None:
            if beat != _beat:
                type_now = note['type']
                index_now += 1
                _beat = beat
                if note['type'] == 'Connection':
                    beat_data.append({
                        "interval": '0',
                        "pixel": note["pixel"],
                        "beat": beat
                    })
                else:
                    interval = Fraction.from_float(beat_now - beat).limit_denominator()
                    beat_now = beat
                    beat_data.append({
                        "interval": interval,
                        "pixel": note["pixel"],
                        "beat": beat
                    })
            
            else:
                if type_now == 'Connection' and note['type'] != 'Connection':
                    beat_data[index_now - 1]['interval'] = Fraction.from_float(beat_now - beat).limit_denominator()
    
    return beat_data

def draw_measure_lines(bpm_data: list[dict[str, Any]], draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    '''绘制小节线'''
    bpm_data = sorted(bpm_data, key=lambda x: x.get("beat", float('inf'))) # 按beat排序
    for idx, data in enumerate(bpm_data):
        pixel_per_beat = get_second(data["bpm"], 1) * config.pps
        y = data["pixel"]
        length = bpm_data[idx + 1]["pixel"] - data["pixel"] if idx + 1 != len(bpm_data) else height - data["pixel"]
        if int(length / pixel_per_beat) + 1 > 0: # 属于该BPM范围的拍数 > 0
            for i in range(int(length / pixel_per_beat) + 1):
                y1 = int(height - (y + config.bpm_line_width // 2)) if int(height - (y + config.bpm_line_width // 2)) != height else height - config.bpm_line_width
                y2 = int(height - (y - config.bpm_line_width // 2)) if int(height - (y - config.bpm_line_width // 2)) != height else height
                draw.rectangle((config.x_sep + config.frame_width, y1, width - config.frame_width - config.x_sep, y2), config.bpm_line_color if i != 0 else config.bpm_line_light_color)
                y += pixel_per_beat
        else: # 属于该BPM范围的拍数 < 0
            for i in range(int(length / pixel_per_beat) + 1, 0, -1): # 负负得正
                y1 = int(height - (y + config.bpm_line_width // 2)) if int(height - (y + config.bpm_line_width // 2)) != height else height - config.bpm_line_width
                y2 = int(height - (y - config.bpm_line_width // 2)) if int(height - (y - config.bpm_line_width // 2)) != height else height
                draw.rectangle((config.x_sep + config.frame_width, y1, width - config.frame_width - config.x_sep, y2), config.bpm_line_color if i != 0 else config.bpm_line_light_color)
                y += pixel_per_beat   

def draw_double_tap_lines(simplified_chart: _ChartType, draw: ImageDraw.ImageDraw, height: int) -> None:
    '''绘制双押线'''
    for data_x in simplified_chart:
        for data_y in simplified_chart:
            if data_x["beat"] == data_y["beat"]:
                x1, y1 = config.x_offset + int(config.frame_width + (data_x["lane"] + 0.5) * config.lane_width), height - (data_x["pixel"] + config.double_beat_line_width // 2)
                x2, y2 = config.x_offset + int(config.frame_width + (data_y["lane"] + 0.5) * config.lane_width), height - (data_y["pixel"] - config.double_beat_line_width // 2)
                if x1 < x2 and y1 < y2:
                    draw.rectangle((config.x_sep + x1, y1, config.x_sep + x2, y2), config.double_beat_line_color)

def draw_notes(chart: _ChartType, chart_img: Image.Image, height: int) -> None:
    '''绘制note'''
    for data in chart:
        if data.get("hidden", False) is True:
            pass

        if data["type"] == "Slide":
            # slide / long
            for idx_c, data_c in enumerate(data["connections"]):
                if idx_c != len(data["connections"]) - 1:
                    # 绘制绿条
                    note_type = "long"
                    x1 = config.x_offset + (config.frame_width + (data_c["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width / 2)
                    x2 = config.x_offset + (config.frame_width + (data["connections"][idx_c + 1]["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width / 2)
                    y1 = data_c["pixel"]
                    y2 = data["connections"][idx_c + 1]["pixel"]
                    k = (x2 - x1) / (y2 - y1) if y2 - y1 != 0 else 0
                    for y in range(data_c["pixel"], data["connections"][idx_c + 1]["pixel"]):
                        b = x2 - (k * y2)
                        x = k * y + b
                        chart_img.paste(skins().skin[note_type], (config.x_sep + int(x) - config.sep_line_width, height - int(y)), skins().skin[note_type])

    for data in chart:
        if data.get("hidden", False) is True:
            pass

        if data["type"] == "Single":
            # tap/flick
            note_type = "flick" if data.get("flick") is True else "tap"
            if note_type == "tap":
                if config.blue_white_tap and not (data["beat"] % 1 == 0 or data["beat"] % 0.5 == 0):
                    # 蓝白键
                    note_type = "tap_white"
                
                if data.get("skill", False):
                    # 技能键
                    note_type = "tap_skill"

                chart_img.paste(
                    skins().skin[note_type],
                    (
                        config.x_sep + int(config.x_offset + (config.frame_width + (data["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width // 2) - config.sep_line_width),
                        height - (data["pixel"] + skins().skin[note_type].height // 2)
                    ),
                    skins().skin[note_type]
                )
            else:
                # flick
                chart_img.paste(
                    skins().skin[note_type],
                    (
                        config.x_sep + int(config.x_offset + (config.frame_width + (data["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width // 2) - config.sep_line_width),
                        height - (data["pixel"] + skins().skin[note_type].height // 2) - config.flick_offset
                    ),
                    skins().skin[note_type]
                )
        
        elif data["type"] == "Directional":
            # 方向键
            note_type = data["direction"].lower() # 小写
            note_symbol = {"left": -1, "right": 1}[note_type] # 用于计算note偏移方向
            note_img = skins().skin[note_type]

            for i in range(data["width"]):
                x = config.x_offset + int(config.frame_width + (data["lane"] + 0.5) * config.lane_width - note_img.width // 2) + config.lane_width * i * note_symbol + config.directional_offset * note_symbol - config.sep_line_width
                y = int(height - (data["pixel"] + note_img.height // 2))
                chart_img.paste(note_img, (config.x_sep + x, y), note_img.split()[-1])
            chart_img.paste(skins().skin[f"{note_type}_arrow"], (config.x_sep + int(x + note_symbol * ((note_img.width if note_symbol == 1 else skins().skin[f"{note_type}_arrow"].width) + config.directional_arrow_offset)), y), skins().skin[f"{note_type}_arrow"])

        elif data["type"] == "Slide":
            # slide / long
            for idx_c, data_c in enumerate(data["connections"]):
                hidden = data_c.get("hidden", False)

                if idx_c != 0 and idx_c != len(data["connections"]) - 1:
                    # 绘制绿条的间隔
                    note_type = "sep"
                    if not hidden:
                        chart_img.paste(skins().skin[note_type], (config.x_sep + config.x_offset + int(config.frame_width + (data_c["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width // 2) - config.sep_line_width, height - (data_c["pixel"] + skins().skin[note_type].height // 2)), skins().skin[note_type])

                if idx_c == 0 or idx_c == len(data["connections"]) - 1:
                    # 绘制绿条的首尾
                    note_type = "flick" if data_c.get("flick") is True else "slide"

                    if data_c.get("skill", False):
                        note_type = "tap_skill"

                    if not hidden:
                        if note_type == "slide" or note_type == "tap_skill":
                            chart_img.paste(
                                skins().skin[note_type],
                                (
                                    config.x_sep + config.x_offset + int(config.frame_width + (data_c["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width // 2) - config.sep_line_width,
                                    height - (data_c["pixel"] + skins().skin[note_type].height // 2)
                                ),
                                skins().skin[note_type]
                            )
                        elif note_type == "flick":
                            chart_img.paste(
                                skins().skin[note_type],
                                (
                                    config.x_sep + config.x_offset + int(config.frame_width + (data_c["lane"] + 0.5) * config.lane_width - skins().skin[note_type].width // 2) - config.sep_line_width,
                                    height - (data_c["pixel"] + skins().skin[note_type].height // 2) - config.flick_offset
                                ),
                                skins().skin[note_type]
                            )

def draw_bpm_texts(bpm_data: list[dict[str, Any]], draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    '''绘制BPM'''
    for idx, data in enumerate(bpm_data):
        x = width - config.x_sep
        y = int(height - data["pixel"] - (config.font().getbbox("114514")[3] if idx == 0 else config.font().getbbox("114514")[3] / 2))
        _bpm = f'{data["bpm"]:.0f}' if isinstance(data["bpm"], int) or data["bpm"].is_integer() else f'{data["bpm"]:.1f}'
        draw.text((x, y), _bpm, config.bpm_text_color, config.font())

def draw_beat_texts(beat_data: list[dict[str, Any]], draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    '''绘制节奏间隔'''
    for idx, data in enumerate(beat_data):
        x = config.x_sep
        y = int(height - data["pixel"] - (config.font().getbbox("114514")[3] if idx == 0 else config.font().getbbox("114514")[3]))
        if data["interval"] != '0':
            if len(splits := str(data['interval']).split('/')) < 2:
                interval = '/1'
            else:
                if splits[0] == '1':
                    interval = f'/{splits[1]}'
                else:
                    if abs(int(splits[0])) < int(splits[1]):
                        interval = f'{splits[0]}/{splits[1]}'
                    else:
                        interval = f'/{splits[1]}'
            draw.text((x, y - 5), interval, config.bpm_text_color, config.font(), 'ra')
            text_bbox = draw.textbbox((x, y), interval, config.font(), 'ra')
            draw.line((text_bbox[0], text_bbox[3], text_bbox[2], text_bbox[3]), config.bpm_text_color, config.bpm_line_width)
        else:
            text_bbox = draw.textbbox((x, y), '0', config.font(), 'ra')
            draw.line((text_bbox[0], text_bbox[3], text_bbox[2], text_bbox[3]), config.bpm_text_color, config.bpm_line_width)

def draw_time_texts(draw: ImageDraw.ImageDraw, height: int):
    '''绘制时间信息'''
    five_seconds_pixel = config.pps * 5
    for i in range(0, height, five_seconds_pixel):
        seconds = i // config.pps
        minutes = seconds // 60
        seconds = seconds % 60
        text = "{:d}:{:02d}".format(minutes, seconds)
        x = int(config.x_sep - config.font().getlength(text))
        y = int(height - i - (config.font().getbbox(text)[3] if i == 0 else config.font().getbbox(text)[3] / 2))
        draw.text((x, y), text, config.time_text_color, config.font())

def draw_note_num(draw: ImageDraw.ImageDraw, width: int, height: int, chart: _ChartType) -> None:
    '''绘制物量信息'''
    simplified_chart = _get_tapable_notes_data(chart)
    simplified_chart = sorted(simplified_chart, key=lambda x: x.get("beat", float('inf')))
    for num in range(49, len(simplified_chart), 50):
        data = simplified_chart[num]
        x = width - config.x_sep
        y = int(height - data["pixel"] - config.font().getbbox("114514")[3] / 2)
        draw.text((x, y), str(num + 1), config.note_num_color, config.font())

def process_image(original_image: Image.Image):   
    '''切割图像到横向'''
    width, height = original_image.size
    _x_sep = int(config.expect_height / config.slice_height * config.x_sep)

    # 计算切片数量
    num_slices = height // config.expect_height
    # 切割图像并保存每个切片
    slices = []
    for i in range(num_slices):
        y_start = i * config.expect_height
        y_end = (i + 1) * config.expect_height
        slice_image = original_image.crop((0, y_start, width, y_end))
        slices.append(slice_image)

    # 从右向左拼接切片图像
    combined_image = Image.new("RGBA", ((width - _x_sep) * num_slices, config.expect_height), (config.bg_color[0], config.bg_color[1], config.bg_color[2], 255))
    x_offset = combined_image.width - _x_sep // 2
    for i, slice_image in enumerate(slices):
        x_offset -= width - _x_sep
        combined_image.paste(slice_image, (x_offset, 0), slice_image)

    return combined_image

__all__ = []

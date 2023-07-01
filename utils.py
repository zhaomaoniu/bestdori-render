from PIL import Image, ImageDraw

from config import *


class Utils:
    def __init__(self) -> None:
        self.frame_color = FRAME_COLOR
        self.frame_width = FRAME_WIDTH
        self.sep_line_color = SEP_LINE_COLOR
        self.sep_line_width = SEP_LINE_WIDTH
        self.color_light_value = COLOR_LIGHT_VALUE
        self.lane_width = LANE_WIDTH
        self.pps = PPS
        self.note_size = NOTE_SIZE
        self.bpm_line_width = BPM_LINE_WIDTH
        self.bpm_line_color = BPM_LINE_COLOR
        self.bpm_line_light_color = BPM_LINE_LIGHT_COLOR
        self.x_offset = X_OFFSET
        self.x_sep = X_SEP
        self.double_beat_line_color = DOUBLE_BEAT_LINE_COLOR
        self.double_beat_line_width = DOUBLE_BEAT_LINE_WIDTH
        self.font = FONT
        self.bpm_text_color = BPM_TEXT_COLOR
        self.time_text_color = TIME_TEXT_COLOR
        self.flick_offset = FLICK_OFFSET
        self.slice_height = SLICE_HEIGHT
        self.directional_offset = DIRECTIONAL_OFFSET
        self.directional_arrow_offset = DIRECTIONAL_ARROW_OFFSET
        self.bg_color = BG_COLOR
        self.note_num_color = NOTE_NUM_COLOR
        self.blue_white_tap = BLUE_WHITE_TAP
        self.lane_num = LANE_NUM
        self.lane_range = LANE_RANGE

        flick = Image.open(f"resources/{SKIN}/flick.png")
        left = Image.open(f"resources/{SKIN}/left.png")
        right = Image.open(f"resources/{SKIN}/right.png")
        left_arrow = Image.open(f"resources/{SKIN}/left_arrow.png")
        right_arrow = Image.open(f"resources/{SKIN}/right_arrow.png")
        self.skin = {
            'flick' : flick.convert("RGBA").resize((self.note_size[0], int(flick.height / flick.width * self.note_size[0])), Image.Resampling.BICUBIC),
            'tap' : Image.open(f"resources/{SKIN}/tap.png").convert("RGBA").resize(self.note_size, Image.Resampling.BICUBIC),
            'tap_white' : Image.open(f"resources/{SKIN}/tap_white.png").convert("RGBA").resize(self.note_size, Image.Resampling.BICUBIC),
            'tap_skill' : Image.open(f"resources/{SKIN}/tap_skill.png").convert("RGBA").resize(self.note_size, Image.Resampling.BICUBIC),
            'slide' : Image.open(f"resources/{SKIN}/slide.png").convert("RGBA").resize(self.note_size, Image.Resampling.BICUBIC),
            'sep': Image.open(f"resources/{SKIN}/sep.png").convert("RGBA").resize(self.note_size, Image.Resampling.BICUBIC),
            'long': Image.open(f"resources/{SKIN}/long.png").convert("RGBA").resize((self.note_size[0], 1), Image.Resampling.BICUBIC),
            'left': left.convert("RGBA").resize((self.note_size[0], int(left.height / left.width * self.note_size[0])), Image.Resampling.BICUBIC),
            'right': right.convert("RGBA").resize((self.note_size[0], int(right.height / right.width * self.note_size[0])), Image.Resampling.BICUBIC),
            'left_arrow': left_arrow.convert("RGBA").resize((int(left_arrow.width / left_arrow.height * (left.height / left.width * self.note_size[0])), int(left.height / left.width * self.note_size[0])), Image.Resampling.BICUBIC),
            'right_arrow': right_arrow.convert("RGBA").resize((int(right_arrow.width / right_arrow.height * (right.height / right.width * self.note_size[0])), int(right.height / right.width * self.note_size[0])), Image.Resampling.BICUBIC),
        }

    def paste(self, background: Image.Image, overlay: Image.Image, box: tuple) -> Image.Image:
        """
        - 将 `overlay` 以 `alpha` 相加的方式粘贴到 `background` 的指定位置上

        :param background: 背景图片
        :param overlay: 需要粘贴的图片
        :param box: 粘贴图片在背景图片的左上角位置

        :return: 返回合并后的图片
        """
        if background.mode != "RGBA" or overlay.mode != "RGBA":
            raise TypeError("The input image must be in RGBA mode.")
        
        paste_x, paste_y = box

        # 创建一个和 background 大小相同的透明图像作为遮罩
        mask = Image.new("L", background.size, 0)
        mask_draw = ImageDraw.Draw(mask)

        # 在遮罩上画一个矩形，矩形的左上角为 (paste_x, paste_y)
        # 矩形的右下角为 (paste_x + overlay.width, paste_y + overlay.height)
        mask_draw.rectangle((paste_x, paste_y, paste_x + overlay.width, paste_y + overlay.height), fill=255)

        # 将 overlay 粘贴到 background 上，只在矩形区域内合并 alpha 值
        background.alpha_composite(overlay, dest=(paste_x, paste_y))

        # 返回合并后的图片
        return background

    def get_second(self, bpm: float, beats: float) -> float:
        '''获取指定BPM的秒数'''
        return beats * (60 / bpm)

    def _get_lighter_color(self, color: tuple) -> tuple:
        '''获取更亮的颜色'''
        if len(color) == 3:
            r, g, b = color
        else:
            r, g, b, a = color
            
        if max([r, g, b]) + self.color_light_value > 255:
            self.color_light_value = 255 - max([r, g, b])
        
        if len(color) == 3:
            return (r + self.color_light_value, g + self.color_light_value, b + self.color_light_value)
        return (r + self.color_light_value, g + self.color_light_value, b + self.color_light_value, a)

    def get_lanes(self, height: int, chart: list):
        '''获取轨道长图'''
        def _round(num):
            # 舍5进6
            if num >= 0:
                return int(num + 0.499999)
            else:
                return int(num - 0.499999)

        if self.lane_num is None or self.lane_range is None:
            # 计算轨道范围和数量
            simplified_chart = []
            for data in chart: # 将slide提到data层次，方便计算
                if data["type"] == "Single" or data["type"] == "Directional":
                    simplified_chart.append(data)

                elif data["type"] == "Slide":
                    for data_c in data["connections"]:
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
            lane_range = self.lane_range
            lane_num = self.lane_num

        width = self.frame_width * 2 + self.lane_width * lane_num
        lanes = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(lanes)

        # 绘制左frame
        draw.rectangle((0, 0, self.frame_width, height), fill=self.frame_color)
        draw.rectangle((self.frame_width // 2, 0, self.frame_width, height), fill=self._get_lighter_color(self.frame_color))
        # 右frame
        draw.rectangle((width - self.frame_width, 0, width, height), fill=self.frame_color)
        draw.rectangle((width - self.frame_width, 0, width - self.frame_width // 2, height), fill=self._get_lighter_color(self.frame_color))

        # 绘制轨道分隔线
        x = self.frame_width - self.sep_line_width // 2
        for i in range(0, lane_num + 1):
            draw.rectangle((x, 0, x + self.sep_line_width, height), self.sep_line_color)
            x += self.lane_width

        result = Image.new("RGBA", (width + self.x_sep * 2, height), self.bg_color)
        result = self.paste(result, lanes, (self.x_sep, 0))

        return result, lane_range
    
    def get_bpm_timepoints(self, chart: list):
        '''获取谱面中所有BPM的timepoint'''
        # 感谢灵喵
        timepoints = list(filter(lambda n: n['type'] == 'BPM', chart)) # 筛选出类型为BPM的数据
        timepoints = sorted(timepoints, key=lambda x: x.get("beat", float('inf'))) # 按beat排序

        for i, data in enumerate(timepoints):
            if i == 0:
                timepoints[i]['time'] = 0
            else:
                timepoints[i]['time'] = timepoints[i - 1]['time'] + (data['beat'] - timepoints[i - 1]['beat']) * (60 / timepoints[i - 1]['bpm'])
        
        return timepoints

    def get_timepoint_base(self, beat, timepoints):
        '''获取指定beat的前一个timepoint'''
        lastBPM = timepoints[0]
        for tp in timepoints:
            if tp['beat'] > beat:
                break
            lastBPM = tp
        return lastBPM
    
    def get_note_time(self, beat, timepoints):
        '''获取note的绝对时间'''
        timepoint = self.get_timepoint_base(beat, timepoints)
        return timepoint["time"] + (beat - timepoint["beat"]) * (60 / timepoint["bpm"])
    
    def preprocess_chart(self, chart: list):
        '''预处理谱面'''
        for data in chart:
            # long 和 slide 在视觉上无异，这里处理成 slide
            if data["type"] == "Long":
                data["type"] = "Slide"

        timepoints = self.get_bpm_timepoints(chart)
        # BPM 更换时间
        
        for idx, data in enumerate(chart):
            # 计算时间和y坐标
            note_type = data["type"]
            
            if note_type == "BPM" or note_type == "Single" or note_type == "Directional":
                chart[idx]["time"] = self.get_note_time(data["beat"], timepoints)
                chart[idx]["pixel"] = int(chart[idx]["time"] * self.pps)

            elif note_type == "Slide":
                for idx_c, data_c in enumerate(data["connections"]):
                    chart[idx]["connections"][idx_c]["time"] = self.get_note_time(data_c["beat"], timepoints)
                    chart[idx]["connections"][idx_c]["pixel"] = int(chart[idx]["connections"][idx_c]["time"] * self.pps)
        
        return chart
    
    def corrent_chart(self, chart: dict, lane_range: tuple):
        '''将负轨修正'''
        if lane_range[0] >= 0:
            # 没有负轨，不需修正
            return chart

        lane_offset = -lane_range[0] # 轨道偏移数

        for idx, data in enumerate(chart):
            note_type = data["type"]

            if note_type == "Single" or note_type == "Directional":
                chart[idx]["lane"] += lane_offset
            
            elif note_type == "Slide":
                for idx_c in range(len(data["connections"])):
                    chart[idx]["connections"][idx_c]["lane"] += lane_offset
        return chart

    def simplify_chart(self, chart: dict):
        '''简化谱面，只保留tap, flick, directional, slide，用于计算双压'''
        simplified_chart = []
        for data in chart:
            if data["type"] == "Single" or data["type"] == "Directional":
                simplified_chart.append(data)

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
    
    def _get_tapable_notes_data(self, chart: dict):
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
    
    def get_height(self, preprocessed_chart: list) -> int:
        '''获取谱面图片高度'''
        max_beat = max([d.get("beat") for d in preprocessed_chart if isinstance(d.get("beat"), (int, float))] +
                    [c.get("beat") for d in preprocessed_chart for c in d.get("connections", []) if isinstance(c.get("beat"), (int, float))])

        data = next((d for d in preprocessed_chart if d.get("beat") == max_beat or any(c.get("beat") == max_beat for c in d.get("connections", []))), None)
        # 最后一个note

        if data["type"] == "BPM" or data["type"] == "Single" or data["type"] == "Directional":
            min_height = data["pixel"] + self.skin["tap"].height
        else:
            min_height = data["connections"][-1]["pixel"] + self.skin["tap"].height

        return int((min_height // self.slice_height + 1) * self.slice_height)

    def get_bpm_data(self, chart: dict):
        '''获取BPM数据，用于绘制BPM文本'''
        bpm_data = []
        for data in chart:
            if data["type"] == "BPM":
                bpm_data.append({
                    "bpm": data["bpm"],
                    "pixel": data["pixel"],
                    "beat": data["beat"]
                })
        return bpm_data

    def draw_measure_lines(self, bpm_data: dict, draw: ImageDraw.ImageDraw, width: int, height: int):
        '''绘制小节线'''
        bpm_data = sorted(bpm_data, key=lambda x: x.get("beat", float('inf'))) # 按beat排序
        for idx, data in enumerate(bpm_data):
            pixel_per_beat = utils.get_second(data["bpm"], 1) * self.pps
            y = data["pixel"]
            length = bpm_data[idx + 1]["pixel"] - data["pixel"] if idx + 1 != len(bpm_data) else height - data["pixel"]
            if int(length / pixel_per_beat) + 1 > 0: # 属于该BPM范围的拍数 > 0
                for i in range(int(length / pixel_per_beat) + 1):
                    y1 = int(height - (y + self.bpm_line_width // 2)) if int(height - (y + self.bpm_line_width // 2)) != height else height - self.bpm_line_width
                    y2 = int(height - (y - self.bpm_line_width // 2)) if int(height - (y - self.bpm_line_width // 2)) != height else height
                    draw.rectangle((self.x_sep + self.frame_width, y1, width - self.frame_width - self.x_sep, y2), self.bpm_line_color if i != 0 else self.bpm_line_light_color)
                    y += pixel_per_beat
            else: # 属于该BPM范围的拍数 < 0
                for i in range(int(length / pixel_per_beat) + 1, 0, -1): # 负负得正
                    y1 = int(height - (y + self.bpm_line_width // 2)) if int(height - (y + self.bpm_line_width // 2)) != height else height - self.bpm_line_width
                    y2 = int(height - (y - self.bpm_line_width // 2)) if int(height - (y - self.bpm_line_width // 2)) != height else height
                    draw.rectangle((self.x_sep + self.frame_width, y1, width - self.frame_width - self.x_sep, y2), self.bpm_line_color if i != 0 else self.bpm_line_light_color)
                    y += pixel_per_beat   

    def draw_double_tap_lines(self, simplified_chart: dict, draw: ImageDraw.ImageDraw, height):
        '''绘制双押线'''
        for data_x in simplified_chart:
            for data_y in simplified_chart:
                if data_x["beat"] == data_y["beat"]:
                    x1, y1 = self.x_offset + int(self.frame_width + (data_x["lane"] + 0.5) * self.lane_width), height - (data_x["pixel"] + self.double_beat_line_width // 2)
                    x2, y2 = self.x_offset + int(self.frame_width + (data_y["lane"] + 0.5) * self.lane_width), height - (data_y["pixel"] - self.double_beat_line_width // 2)
                    if x1 < x2 and y1 < y2:
                        draw.rectangle((self.x_sep + x1, y1, self.x_sep + x2, y2), self.double_beat_line_color)

    def draw_notes(self, chart: dict, chart_img: Image.Image, height: int):
        '''绘制note'''
        for data in chart:
            if data.get("hidden", False) is True:
                pass

            if data["type"] == "Single":
                # tap/flick
                note_type = "flick" if data.get("flick") is True else "tap"
                if note_type == "tap":
                    if self.blue_white_tap and not (data["beat"] % 1 == 0 or data["beat"] % 0.5 == 0):
                        # 蓝白键
                        note_type = "tap_white"
                    
                    if data.get("skill", False):
                        # 技能键
                        note_type = "tap_skill"

                    chart_img.paste(self.skin[note_type], (self.x_sep + int(self.x_offset + (self.frame_width + (data["lane"] + 0.5) * self.lane_width - self.skin[note_type].width // 2) - self.sep_line_width), height - (data["pixel"] + self.skin[note_type].height // 2)), self.skin[note_type])
                else:
                    # flick
                    chart_img.paste(self.skin[note_type], (self.x_sep + int(self.x_offset + (self.frame_width + (data["lane"] + 0.5) * self.lane_width - self.skin[note_type].width // 2) - self.sep_line_width), height - (data["pixel"] + self.skin[note_type].height // 2) - self.flick_offset), self.skin[note_type])
            
            elif data["type"] == "Directional":
                # 方向键
                note_type = data["direction"].lower() # 小写
                note_symbol = {"left": -1, "right": 1}[note_type] # 用于计算note偏移方向
                note_img = self.skin[note_type]

                for i in range(data["width"]):
                    x = self.x_offset + int(self.frame_width + (data["lane"] + 0.5) * self.lane_width - note_img.width // 2) + self.lane_width * i * note_symbol + self.directional_offset * note_symbol - self.sep_line_width
                    y = int(height - (data["pixel"] + note_img.height // 2))
                    chart_img.paste(note_img, (self.x_sep + x, y), note_img.split()[-1])
                chart_img.paste(self.skin[f"{note_type}_arrow"], (self.x_sep + int(x + note_symbol * ((note_img.width if note_symbol == 1 else self.skin[f"{note_type}_arrow"].width) + self.directional_arrow_offset)), y), self.skin[f"{note_type}_arrow"])

            elif data["type"] == "Slide":
                # slide / long
                for idx_c, data_c in enumerate(data["connections"]):
                    hidden = data_c.get("hidden", False)

                    if idx_c != len(data["connections"]) - 1:
                        # 绘制绿条
                        note_type = "long"
                        x1 = self.x_offset + (self.frame_width + (data_c["lane"] + 0.5) * self.lane_width - self.skin[note_type].width / 2)
                        x2 = self.x_offset + (self.frame_width + (data["connections"][idx_c + 1]["lane"] + 0.5) * self.lane_width - self.skin[note_type].width / 2)
                        y1 = data_c["pixel"]
                        y2 = data["connections"][idx_c + 1]["pixel"]
                        k = (x2 - x1) / (y2 - y1) if y2 - y1 != 0 else 0
                        for y in range(data_c["pixel"], data["connections"][idx_c + 1]["pixel"]):
                            b = x2 - (k * y2)
                            x = k * y + b
                            chart_img.paste(self.skin[note_type], (self.x_sep + int(x) - self.sep_line_width, height - int(y)), self.skin[note_type])

                    if idx_c != 0 and idx_c != len(data["connections"]) - 1:
                        # 绘制绿条的间隔
                        note_type = "sep"
                        if not hidden:
                            chart_img.paste(self.skin[note_type], (self.x_sep + self.x_offset + int(self.frame_width + (data_c["lane"] + 0.5) * self.lane_width - self.skin[note_type].width // 2) - self.sep_line_width, height - (data_c["pixel"] + self.skin[note_type].height // 2)), self.skin[note_type])

                    if idx_c == 0 or idx_c == len(data["connections"]) - 1:
                        # 绘制绿条的首尾
                        note_type = "flick" if data_c.get("flick") is True else "slide"

                        if data_c.get("skill", False):
                            note_type = "tap_skill"

                        if not hidden:
                            if note_type == "slide" or note_type == "tap_skill":
                                chart_img.paste(self.skin[note_type], (self.x_sep + self.x_offset + int(self.frame_width + (data_c["lane"] + 0.5) * self.lane_width - self.skin[note_type].width // 2) - self.sep_line_width, height - (data_c["pixel"] + self.skin[note_type].height // 2)), self.skin[note_type])
                            elif note_type == "flick":
                                chart_img.paste(self.skin[note_type], (self.x_sep + self.x_offset + int(self.frame_width + (data_c["lane"] + 0.5) * self.lane_width - self.skin[note_type].width // 2) - self.sep_line_width, height - (data_c["pixel"] + self.skin[note_type].height // 2) - self.flick_offset), self.skin[note_type])

    def draw_bpm_texts(self, bpm_data: dict, draw: ImageDraw.ImageDraw, width: int, height: int):
        '''绘制BPM'''
        for idx, data in enumerate(bpm_data):
            x = width - self.x_sep
            y = int(height - data["pixel"] - (self.font.getbbox("114514")[3] if idx == 0 else self.font.getbbox("114514")[3] / 2))
            draw.text((x, y), str(data["bpm"]), self.bpm_text_color, self.font)

    def draw_time_texts(self, draw: ImageDraw.ImageDraw, height: int):
        '''绘制时间信息'''
        five_seconds_pixel = self.pps * 5
        for i in range(0, height, five_seconds_pixel):
            seconds = i // self.pps
            minutes = seconds // 60
            seconds = seconds % 60
            text = "{:d}:{:02d}".format(minutes, seconds)
            x = int(self.x_sep - self.font.getlength(text))
            y = int(height - i - (self.font.getbbox(text)[3] if i == 0 else self.font.getbbox(text)[3] / 2))
            draw.text((x, y), text, self.time_text_color, self.font)

    def draw_note_num(self, draw: ImageDraw.ImageDraw, width: int, height: int, chart: list):
        '''绘制物量信息'''
        simplified_chart = self._get_tapable_notes_data(chart)
        simplified_chart = sorted(simplified_chart, key=lambda x: x.get("beat", float('inf')))
        for num in range(50, len(simplified_chart) + 1, 50):
            data = simplified_chart[num]
            x = width - self.x_sep
            y = int(height - data["pixel"] - self.font.getbbox("114514")[3] / 2)
            draw.text((x, y), str(num), self.note_num_color, self.font)

    def process_image(self, original_image: Image.Image):   
        '''切割图像到横向'''     
        width, height = original_image.size

        # 计算切片数量
        num_slices = height // self.slice_height

        # 切割图像并保存每个切片
        slices = []
        for i in range(num_slices):
            y_start = i * self.slice_height
            y_end = (i + 1) * self.slice_height
            slice_image = original_image.crop((0, y_start, width, y_end))
            slices.append(slice_image)

        # 从右向左拼接切片图像
        combined_image = Image.new("RGBA", (width * num_slices, self.slice_height))
        x_offset = width * num_slices
        for i, slice_image in enumerate(slices):
            x_offset -= width
            combined_image.paste(slice_image, (x_offset, 0))

        return combined_image
    
utils = Utils()

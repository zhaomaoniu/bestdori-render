import json

from PIL import Image, ImageDraw

from utils import utils
from config import *


def render(data: dict) -> Image.Image:
    '''
    渲染BanG Dream谱面
    
    `data`: Bestdori谱面数据
    '''
    chart = utils.preprocess_chart(data)
    height = utils.get_height(chart)
    chart_img, lane_range = utils.get_lanes(height, chart)

    chart = utils.corrent_chart(chart, lane_range)
    simplified_chart = utils.simplify_chart(chart)

    draw = ImageDraw.Draw(chart_img)

    bpm_data = utils.get_bpm_data(chart)

    utils.draw_measure_lines(bpm_data, draw, chart_img.width, height)
    utils.draw_double_tap_lines(simplified_chart, draw, height)
    utils.draw_notes(chart, chart_img, height)

    utils.draw_bpm_texts(bpm_data, draw, chart_img.width, height)
    utils.draw_time_texts(draw, height)
    utils.draw_note_num(draw, chart_img.width, height, chart)

    result = utils.process_image(chart_img)
    result = result.resize((int(result.width / result.height * EXPECT_HEIGHT), EXPECT_HEIGHT))

    bg = Image.new("RGBA", result.size, BG_COLOR)

    return utils.paste(bg, result, (0, 0))


with open("expert.json", "r", encoding="UTF-8") as f:
    data = json.load(f)

render(data).save("temp.png")

from PIL import Image, ImageDraw
from bestdori.charts import Chart

from ._utils import Utils
from .config import Config, get_config


def render(chart: Chart, config: Config = get_config()) -> Image.Image:
    """
    渲染BanG Dream谱面

    参数:
        chart: 谱面对象 `bestdori.charts.Chart`
    """
    utils = Utils(config)

    chart_data = chart.to_list()
    chart_data = utils.preprocess_chart(chart_data)
    height = utils.get_height(chart_data)
    chart_img, lane_range = utils.get_lanes(height, chart_data)

    chart_data = utils.corrent_chart(chart_data, lane_range)
    simplified_chart = utils.simplify_chart(chart_data)

    draw = ImageDraw.Draw(chart_img)

    bpm_data = utils.get_bpm_data(chart_data)
    beat_data = utils.get_beat_data(chart_data)

    utils.draw_measure_lines(bpm_data, draw, chart_img.width, height)
    utils.draw_double_tap_lines(simplified_chart, draw, height)
    utils.draw_notes(chart_data, chart_img, height)

    utils.draw_bpm_texts(bpm_data, draw, chart_img.width, height)
    utils.draw_beat_texts(beat_data, draw, chart_img.width, height)
    utils.draw_time_texts(draw, height)
    utils.draw_note_num(draw, chart_img.width, height, chart_data)

    result = utils.process_image(chart_img)
    result = result.resize(
        (
            int(result.width / result.height * config["expect_height"]),
            config["expect_height"],
        )
    )

    bg = Image.new("RGBA", result.size, config["bg_color"])

    return utils.paste(bg, result, (0, 0))


__all__ = ["render"]

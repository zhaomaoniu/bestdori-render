from PIL import Image, ImageDraw
from bestdori.charts import Chart
from typing import Union, List, Dict, Any

from . import _utils as utils
from . import config


def render(chart: Union[Chart, List[Dict[str, Any]]]) -> Image.Image:
    """Render BanG Dream chart
    
    Args:
        chart: Chart object `bestdori.charts.Chart` or chart data
    
    Returns:
        Image: Rendered BanG Dream chart
    """

    chart_data = chart.to_list() if isinstance(chart, Chart) else chart
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
    
    _expect_sum_height = chart_img.height // config.slice_height * config.expect_height
    chart_img = chart_img.resize((int(chart_img.width / chart_img.height * _expect_sum_height), _expect_sum_height), Image.Resampling.BILINEAR)
    
    result = utils.process_image(chart_img)
    
    return result


__all__ = [
    "render",
    "config"
]

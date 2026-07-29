from flask import Flask, request, jsonify, render_template

from src.color_utils import ColorUtils
from src.image_utils import ImageUtils


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['GET', 'POST'])
def api_generate():
    """接收主色hex值，返回配色方案列表"""
    hex_color = request.json.get('color')
    mode = request.json.get('mode')

    # 调用调色器
    cu = ColorUtils(hex_color)
    palette = cu.calculate_palette_from_hex(mode)
    return palette

@app.route('/api/extract', methods=['GET', 'POST'])
def api_extract():
    """提取颜色的主色调"""
    img_file = request.files['image'].read()

    # 调用图片处理器
    iu = ImageUtils(img_file)
    color = iu.get_palette()
    return  color[0]

if __name__ == "__main__":
    app.run('host/port/debug')

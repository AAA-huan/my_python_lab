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

    # 校验参数
    if not hex_color or not mode:
        return jsonify({'error': '参数错误'}), 400

    # 校验模式
    if mode not in ['hex', 'rgb']:
        return jsonify({'error': '模式错误'}), 400

    # 校验hex值
    if not hex_color.startswith('#') or len(hex_color) != 7:
        return jsonify({'error': 'hex值错误'}), 400

    # 调用调色器
    cu = ColorUtils(hex_color)
    palette = cu.calculate_palette_from_hex(mode)
    data = {
        'palette': palette
    }
    return jsonify(data)

@app.route('/api/extract', methods=['GET', 'POST'])
def api_extract():
    """提取颜色的主色调"""
    img_file = request.files['image']

    # 校验图片文件
    if not img_file.filename:
        return jsonify({'error': '图片文件错误'}), 400
    
    # 校验图片文件类型
    if not img_file.filename.endswith('.jpg') and not img_file.filename.endswith('.jpeg') and not img_file.filename.endswith('.png'):
        return jsonify({'error': '图片文件类型错误'}), 400

    # 调用图片处理器
    iu = ImageUtils(img_file.read())
    color = iu.get_palette()
    data = {
        'color': color[0]
    }
    return  jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

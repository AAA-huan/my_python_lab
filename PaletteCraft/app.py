import os
import dotenv
from flask import Flask, request, jsonify, render_template

from src.color_utils import ColorUtils
from src.image_utils import ImageUtils


dotenv.load_dotenv('../.env')
# 子站只需绑定配置，不需要对外地址（它不生成跳转URL）
BIND_HOST = os.getenv('BIND_HOST', '0.0.0.0')
PALETTE_SERVER_PORT = os.getenv('PALETTE_SERVER_PORT', '5001')
DEBUG = os.getenv('DEBUG')


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['GET', 'POST'])
def api_generate():

    #
    # 1. 优先尝试从 JSON Body 中获取数据 (适配你现在的手机前端)
    data = request.get_json(silent=True)

    # 2. 如果 JSON 为空，再尝试从 URL 参数获取 (保留对 GET 请求的兼容)
    if not data:
        data = request.args

    # 3. 从统一的数据源中提取参数
    hex_color = data.get('color')
    mode = data.get('mode')

    # --- 以下是你原本的校验逻辑 ---
    if not hex_color or not mode:
        return jsonify({'error': '参数错误'}), 400
    print(f"Args: {request.args}")
    print(f"Form: {request.form}")
    print(f"JSON: {request.get_json(silent=True)}")
    #

    # 校验参数
    if not hex_color or not mode:
        return jsonify({'error': '参数错误'}), 400

    # 校验模式
    if mode not in ['complementary', 'analogous', 'triadic']:
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
    app.run(host=BIND_HOST, port=PALETTE_SERVER_PORT, debug=DEBUG)

import dotenv
import os
from flask import Flask, redirect, render_template


dotenv.load_dotenv('.env')
# 绑定配置
BIND_HOST = os.getenv('BIND_HOST', '0.0.0.0')
MAIN_SERVER_PORT = os.getenv('MAIN_SERVER_PORT', '5000')
PALETTE_SERVER_PORT = os.getenv('PALETTE_SERVER_PORT', '5001')
DEBUG = os.getenv('DEBUG')

# 对外访问配置
PUBLIC_HOST = os.getenv('PUBLIC_HOST', '127.0.0.1')
PUBLIC_PROTO = os.getenv('PUBLIC_PROTO', 'http')
# 反代场景下对外端口，留空则用服务真实端口
PUBLIC_PORT = os.getenv('PUBLIC_PORT', '') or PALETTE_SERVER_PORT


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/go_palette', methods=['GET'])
def go_palette():
    """跳转到子站palette"""
    return redirect(f'{PUBLIC_PROTO}://{PUBLIC_HOST}:{PUBLIC_PORT}/')

if __name__ == '__main__':
    app.run(host=BIND_HOST, port=MAIN_SERVER_PORT, debug=DEBUG)




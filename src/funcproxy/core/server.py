# src/hook_tool/core/server.py
import logging
from threading import Lock
from flask import Flask, request, Response, send_file
from flask import render_template, stream_with_context, jsonify
from flask_cors import CORS
import json
import os
import pkg_resources
from pathlib import Path
from gevent.pywsgi import WSGIServer

from .plugin import PluginManager
from .lib import proxy_stream_request, generate_fake_response
from .lib import extensions
from .lib import load_config, save_config


logger = logging.getLogger("funcproxy")
logger.addHandler(logging.StreamHandler())

def start_server(port: int = 8000, plugin_dir: str = "plugins", debug: bool = False):
    """启动带插件系统的 HTTP 服务器
    Args:
        port: 监听端口
        plugin_dir: 插件目录路径
        debug: 是否启用调试模式
    """
    app = Flask(__name__)
    CORS(app)
    plugin_manager = PluginManager()
    reload_lock = Lock()  # 插件重载的线程锁

    # 初始化插件系统
    try:
        plugin_manager.load_plugins_from_dir()
        logger.info(f"Loaded plugins from {plugin_dir}")
    except Exception as e:
        logger.error(f"Initial plugin loading failed: {str(e)}")

    # 设置模板目录
    template_folder = pkg_resources.resource_filename(__name__, 'templates')
    app.template_folder = template_folder

    # 设置静态资源目录
    static_folder = pkg_resources.resource_filename(__name__, 'static')
    app.static_folder = static_folder
    @app.route('/')
    def extension_home():
        return render_template("extensions.html")
    
    @app.route('/icon')
    def get_icon_img():
        if request.method == 'GET':
            plugin_path = Path(__file__).parent.parent / "plugins"
            print(plugin_path)
            plugin_id = request.args.get('id','404')
            icon_path = os.path.join( plugin_path , plugin_id , "icon.png")
            if os.path.exists(icon_path):
                return send_file(icon_path)
            return jsonify({"error": "icon not found"}),404
            

    @app.route('/extension-detail.html')
    def extension_detail():
        return render_template("extension-detail.html")
    
    @app.route('/settings.html')
    def settings_page():
        return render_template("settings.html")
    
    @app.route('/api/extensions')
    def get_extensions():
        return jsonify(extensions)
    
    @app.route('/api/extensions/<string:ext_id>', methods=['GET', 'DELETE', 'PATCH'])
    def get_extension(ext_id):
        ext = next((e for e in extensions if e["id"] == ext_id), None)
        if not ext:
                return jsonify({"error": "Extension not found"}), 404
        if request.method == 'GET':
            detail = ext.copy()
            detail.update({
                "author": "Example Developer",
                "website": "https://example.com",
                "full_description": f"{ext['description']} 更多详细信息...",
                "rating": 4.8
            })
            return jsonify(detail)
        if request.method == 'DELETE':
            return jsonify({"success": True})
        if request.method == 'PATCH':
            ext['enabled'] = not ext['enabled']
            return jsonify({"success": True, "newStatus": ext['enabled']})

    @app.route('/api/settings', methods=['GET','POST'])
    def api_settings():
        app_settings = load_config()
        if request.method == 'GET':
            return jsonify(app_settings)
        if request.method == 'POST':
            data = request.json
            app_settings.update({
                "apiDomain": data.get('apiDomain', app_settings['apiDomain']),
                "apiKey": data.get('apiKey', app_settings['apiKey']),
                "modelName": data.get('modelName', app_settings['modelName'])
            })
            save_config(app_settings)
            return jsonify({"status": "success"})
    @app.route('/v1/chat/completions', methods=['POST'])
    def chat_completions():
        data = request.get_json()
        stream = data.get("stream", False)
        # print(json.dumps(data))
        # print(request.headers)
        if stream:
            return stream_with_context(proxy_stream_request(request))
        return jsonify(generate_fake_response("model"))

    # 配置请求处理管道
    @app.before_request
    def before_request_hooks():
        """处理所有请求的前置钩子"""
        with reload_lock:
            # 将 Flask 请求转换为通用字典格式
            req_data = {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "body": request.get_data(),
                "args": dict(request.args)
            }

    # 添加调试端点（仅限调试模式）
    if debug:
        @app.route('/_hook_tool/status')
        def status():
            return {
                "status": "running",
                "plugins": [type(h).__name__ for h in plugin_manager.hooks]
            }

    try:
        logger.info(f"Starting server on port {port}")
        http_server = WSGIServer(('0.0.0.0', port), app)
        http_server.serve_forever()
    finally:
        logger.info("Server stopped")
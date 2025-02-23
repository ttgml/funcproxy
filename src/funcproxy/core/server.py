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
import zipfile
import tempfile
import shutil

from .plugin import PluginManager
from .lib import process_stream_request, process_standard_request

from .lib import load_config, save_config


logger = logging.getLogger("funcproxy")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def start_server(port: int = 8000, plugin_dir: str = "plugins", debug: bool = False):
    """启动带插件系统的 HTTP 服务器"""
    app = Flask(__name__)
    CORS(app)
    plugin_manager = PluginManager()
    reload_lock = Lock()  # 插件重载的线程锁
    app.plugin_manager = plugin_manager

    # 初始化插件系统
    try:
        plugin_manager.load_plugins_from_dir()
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
        extensions = plugin_manager.get_plugins()
        return jsonify(extensions)
    
    @app.route('/api/extensions/<string:ext_id>', methods=['GET', 'DELETE', 'PATCH', 'POST'])
    def get_extension(ext_id):
        extensions = plugin_manager.get_plugins()
        ext = next((e for e in extensions if e["id"] == ext_id), None)
        if not ext:
                return jsonify({"error": "Extension not found"}), 404
        if request.method == 'GET':
            detail = ext.copy()
            detail['settings'] = plugin_manager.get_plugin_settings(ext_id)
            detail.update({
                "full_description": f"{ext['description']} 更多详细信息...",
                "rating": 4.8
            })
            return jsonify(detail)
        if request.method == 'DELETE':
            return jsonify({"success": True})
        if request.method == 'PATCH':
            ext['enabled'] = not ext['enabled']
            if ext['enabled'] == True:
                plugin_manager.enable_plugin(ext['id'])
            else:
                plugin_manager.disable_plugin(ext['id'])
            return jsonify({"success": True, "newStatus": ext['enabled']})
        if request.method == 'POST':
            plugin_manager.update_plugin_settings(ext['id'], request.json)
            return jsonify({"success": True})

    @app.route('/api/settings', methods=['GET','POST'])
    def api_settings():
        app_settings = load_config()
        if request.method == 'GET':
            return jsonify(app_settings)
        if request.method == 'POST':
            data = request.json
            try:
                if data.get('apiDomain')[-1] == '/':
                    data['apiDomain'] = data['apiDomain'][:-1]
                app_settings.update({
                    "apiDomain": data.get('apiDomain', app_settings['apiDomain']),
                    "apiKey": data.get('apiKey', app_settings['apiKey']),
                    "modelName": data.get('modelName', app_settings['modelName'])
                })
                save_config(app_settings)
            except Exception as e:
                logger.error(f"Failed to update settings: {str(e)}")
                return jsonify({"status": "error", "message": "Failed to update settings"}),400
            return jsonify({"status": "success"})
    @app.route('/upload/plugin', methods=['POST'])
    def upload_plugin():
        if request.method == 'POST':
            file = request.files['file']
            # 检查文件类型，是否是zip文件
            if file and file.filename.endswith('.zip'):
                # 解压文件到临时目录
                temp_dir = tempfile.mkdtemp()
                file.save(os.path.join(temp_dir, file.filename))
                with zipfile.ZipFile(os.path.join(temp_dir, file.filename), 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                print(temp_dir)
                install_result = plugin_manager.install_plugin(temp_dir)
                print("install result: ", install_result)
                shutil.rmtree(temp_dir)
                if install_result == None:
                    plugin_manager.init_plugins()
                    return jsonify({"status": "success", "message": "插件上传成功"})
                else:
                    return jsonify({"status": "error", "message": install_result['error']}),400
    @app.route('/v1/chat/completions', methods=['POST'])
    def chat_completions():
        data = request.get_json()
        stream = data.get("stream", False)
        # print(json.dumps(data))
        # print(request.headers)
        if stream:
            return stream_with_context(process_stream_request(request))
        else:
            return jsonify(process_standard_request(request))

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
                "status": "running"
            }

    try:
        logger.info(f"Starting server on port {port}")
        http_server = WSGIServer(('0.0.0.0', port), app)
        http_server.serve_forever()
    finally:
        logger.info("Server stopped")
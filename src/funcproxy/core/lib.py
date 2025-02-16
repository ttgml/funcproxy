import time
import uuid
import json
import logging
import os

def generate_fake_response(model):
    """生成模拟的OpenAI响应结构"""
    return {
        "id": "chatcmpl-" + str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "这是一个模拟的OpenAI响应（非流式）"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

def generate_stream_response(model, delay=0.2):
    content_chunks = ["这是", "一个", "模拟的", "OpenAI", "流式", "响应"]
    for index, chunk in enumerate(content_chunks):
        data = {
            "id": "chatcmpl-" + str(uuid.uuid4()),
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {
                    "content": chunk
                },
                "finish_reason": None if index < len(content_chunks)-1 else "stop"
            }]
        }
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(delay)
    yield "data: [DONE]\n\n"


def load_config(CONFIG_FILE_PATH):
    """从配置文件中加载设置"""
    print(f"Loading config from {CONFIG_FILE_PATH}")
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as f:
            return json.load(f)
    else:
        return {
            "apiDomain": "https://api.default.com",
            "apiKey": "",
            "modelName": ""
        }

def save_config(config, CONFIG_FILE_PATH):
    """将设置保存到配置文件中"""
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(config, f, indent=4)


extensions = [
            {
                "id": "adblock",
                "icon": "https://via.placeholder.com/48",
                "title": "AdBlock - 最佳广告拦截工具",
                "description": "拦截网页上的广告和弹窗，提升浏览体验",
                "version": "5.15.0",
                "size": "3.2MB",
                "updated": "2024-02-15",
                "enabled": True
            },
            {
                "id": "grammarly",
                "icon": "https://via.placeholder.com/48",
                "title": "Grammarly for Chrome",
                "description": "实时语法检查和写作建议",
                "version": "1.45.2",
                "size": "15.8MB",
                "updated": "2024-02-10",
                "enabled": False
            }
        ]
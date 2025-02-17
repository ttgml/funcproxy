import time
import uuid
import json
import logging
import os
from flask import Request
import requests

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

def proxy_stream_request(request: Request):
    data = request.get_json()
    proxy_config = load_config()
    # print(proxy_config)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    }
                }
            }
        }
    ]

    data['model'] = proxy_config['modelName']
    data["tools"] = tools
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {proxy_config['apiKey']}"
    }
    url = f"{proxy_config['apiDomain']}/v1/chat/completions"
    response = requests.post(url, json=data, headers=headers, stream=True)

    current_tool_call = {
        "id": None,          # 当前工具调用的唯一ID
        "function": {
            "name": "",      # 逐步累积的函数名
            "arguments": ""  # 逐步累积的参数JSON字符串
        }
    }
    
    try:
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8')
                if chunk_str.startswith('data: '):
                    json_str = chunk_str[len('data: '):]
                    if json_str.strip() == "[DONE]":
                        break
                    try:
                        json_obj = json.loads(json_str)
                        choice = json_obj.get('choices', [{}])[0]
                        delta = choice.get('delta', {})
                        if "content" in delta:
                            print(chunk_str)
                            yield chunk_str + "\n\n"
                        if "tool_calls" in delta :
                            tool_calls = delta["tool_calls"][0]
                            if "function" in tool_calls and "name" in tool_calls["function"]:
                                current_tool_call["function"]["name"] += tool_calls["function"]["name"]
                            if "function" in tool_calls and "arguments" in tool_calls["function"]:
                                current_tool_call["function"]["arguments"] += tool_calls["function"]["arguments"]
                            if "id" in tool_calls:
                                current_tool_call["id"] = tool_calls["id"]
                        content = json_obj['choices'][0]['delta'].get('content', '')
                        # print("Content: ",content)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {chunk_str}")
                else:
                    print(f"Unexpected chunk: {chunk_str}")
        print(current_tool_call)
    except Exception as e:
        print(f"Error: ", e)
    finally:
        response.close()


def load_config():
    """从配置文件中加载设置"""
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
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

def save_config(config):
    """将设置保存到配置文件中"""
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
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
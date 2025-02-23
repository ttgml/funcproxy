import time
import uuid
import json
import logging
import os
from flask import Request, current_app
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

def generate_standard_response(content:str, model="funcproxy"):
    obj = {
        "id": "chatcmpl-" + str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": str(content)
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

def process_standard_request(request: Request) -> dict:
    data = request.get_json()
    proxy_config = load_config()

    plugin_manager = get_plugin_manager()
    tools = []
    for tool_name, plugin_name in plugin_manager.tools.items():
        print("tools name: ", tools, plugin_name)
        tools = plugin_manager.enabled_plugins[plugin_name].add_function(tools)
    data['model'] = proxy_config['modelName']
    if len(tools) > 0:
        data["tools"] = tools
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {proxy_config['apiKey']}"
    }
    url = f"{proxy_config['apiDomain']}/v1/chat/completions"
    process_session = True
    while process_session:
        try:
            response = requests.post(url, json=data, headers=headers, stream=False)
            final_tool_calls = {}
            print("data: ",json.dumps(data))
            resp = response.json()
            print("resp: ",json.dumps(resp))
            for ms in resp['choices']:
                if ms['message'].get('tool_calls', None) == None:
                    return response.json()
                for function_call in ms['message']['tool_calls']:
                    if function_call['type'] == 'function':
                        for tool_name, plugin_name in plugin_manager.tools.items():
                            if function_call['function']['name'] == tool_name:
                                final_tool_calls[function_call['id']] = function_call
                                result = ""
                                arguments = function_call['function'].get('arguments',[])
                                data['messages'].append(generate_function_message(function_call))
                                try:
                                    plugin = getattr(plugin_manager.enabled_plugins[plugin_name], tool_name)
                                    print("arguments: ", arguments)
                                    result = plugin(arguments)
                                except Exception as e:
                                    print("Error: ", e)
                                    result = "Error: " + str(e)
                                data['messages'].append({"role": "tool", "content": result, "tool_call_id": function_call['id']})                    
        except Exception as e:
            print("Error: ", e)
            return {}
    print("process end")
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

def generate_stream_data(id: str, model:str, content: str, finish_reason: str):
    fake_response_data = {
        "id": id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {
                "content": content,
                "role": "assistant"
            },
            "finish_reason": None
        }]
    }
    fake_response_data = json.dumps(fake_response_data)
    return fake_response_data

def generate_function_message(tool_call: dict):
    obj = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": tool_call["id"],
            "type": "function",
            "function": {
                "name": tool_call["function"]["name"],
                "arguments": tool_call["function"]["arguments"]
            }
        }]
    }
    return obj

def get_plugin_manager():
    return current_app.plugin_manager
def process_stream_request(request: Request):
    data = request.get_json()
    proxy_config = load_config()
    # print(proxy_config)

    plugin_manager = get_plugin_manager()
    tools = []
    for tool_name, plugin_name in plugin_manager.tools.items():
        print("tools name: ", tools, plugin_name)
        tools = plugin_manager.enabled_plugins[plugin_name].add_function(tools)
    print("tools result: ", tools)
    data['model'] = proxy_config['modelName']
    if len(tools) > 0:
        data["tools"] = tools
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {proxy_config['apiKey']}"
    }
    url = f"{proxy_config['apiDomain']}/v1/chat/completions"

    process_session = True
    while process_session:
        response = requests.post(url, json=data, headers=headers, stream=True)
        final_tool_calls = {}
        try:
            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    if chunk_str.startswith('data: '):
                        json_str = chunk_str[len('data: '):]
                        if json_str.strip() == "[DONE]":
                            if final_tool_calls == {}:
                                process_session = False
                            else:
                                for i in final_tool_calls.keys():
                                    data['messages'].append(generate_function_message(final_tool_calls[i]))
                                    result = ""
                                    arguments = final_tool_calls[i]['function'].get('arguments',[])
                                    if final_tool_calls[i]['function']['name'] == "get_current_weather":
                                        result = "23 °C"
                                    if final_tool_calls[i]['function']['name'] == "get_current_location":
                                        result = "北京"
                                    if final_tool_calls[i]['function']['name'] == "get_wallet_balance":
                                        result = "2000 Dollars"
                                    for tool_name, plugin_name in plugin_manager.tools.items():
                                        if final_tool_calls[i]['function']['name'] == tool_name:
                                            plugin = getattr(plugin_manager.enabled_plugins[plugin_name], tool_name)
                                            print("callit: ", final_tool_calls[i])
                                            result = str(plugin(arguments))
                                    print("result: ", result)
                                    data['messages'].append({"role": "tool", "content": result, "tool_call_id": final_tool_calls[i]['id']})
                                process_session = True
                            break
                        else:
                            try:
                                json_obj = json.loads(json_str)
                                choice = json_obj.get('choices', [{}])[0]
                                delta = choice.get('delta', {})
                                if "content" in delta:
                                    if delta["content"] != None:
                                        yield chunk_str + "\n\n"
                                if "tool_calls" in delta :
                                    for tool_call in delta["tool_calls"]:
                                        index = tool_call['index']
                                        if index not in final_tool_calls:
                                            final_tool_calls[index] = tool_call
                                            # print("tool_call: ", tool_call)
                                        else:
                                            if "name" in tool_call['function']:
                                                if tool_call['function']['name'] != None:
                                                    final_tool_calls[index]['function']['name'] += tool_call['function']['name']
                                            if "arguments" in tool_call['function']:
                                                if tool_call['function']['arguments'] != None:
                                                    final_tool_calls[index]['function']['arguments'] += tool_call['function']['arguments']
                            except json.JSONDecodeError:
                                print(f"Invalid JSON: {chunk_str}")
                    else:
                        print(f"Unexpected chunk: {chunk_str}")
                        process_session = False
                        break
        except Exception as e:
            print(f"Error: ", e)
        finally:
            response.close()
    print("process end")


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

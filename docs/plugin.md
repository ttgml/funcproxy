## 开发扩展

1. 创建一个文件夹，例如`my_extension`
2. 在该文件夹下创建一个`info.json`文件，并添加以下内容：
```json
{
    "description": "扩展说明",
    "enabled": false,
    "func": [ // 定义 function tool 
        {
            "description": "get system version info", //Function tool 描述
            "func": "do_example_tool_call", //tool 函数名 ** 需要在__init__.py中实现
            "name": "获取系统版本信息", //tool 名称
            "parameters": { //tool 参数
                "properties": {
                    "item": {
                        "description": "anything",
                        "type": "string"
                    }
                },
                "required": [
                    "item"
                ],
                "type": "object"
            }
        }
    ],
    "icon": "/icon?id=example_extension",
    "id": "example_extension", //id需要和plugin下的文件夹名称一致
    "size": "0.01MB",
    "title": "example 扩展名字",
    "type": "func",
    "updated": "2025-02-20",
    "version": "0.0.1",
    "author": "Example Developer",
    "website": "https://example.com"
}

```

3. 在`my_extension`文件夹下创建一个`__init__.py`文件，并添加以下内容：
```python
from funcproxy.core.plugin_base import PluginBase
class Plugin(PluginBase):
    # 继承PluginBase类，实现函数
    def do_example_tool_call(self, parameters) -> str:
        pass

```

4. [可选]如果扩展需要引入配置项的话，可以在`my_extension`文件夹下创建 setting.json 文件，并添加以下内容，在扩展详情页面会自动生成表单：
```json
{
    "current": {
        "apikey": ""
    },

    "form": [
        {
            "default": "",
            "label": "API KEY",
            "name": "apikey",
            "placeholder": "API KEY",
            "required": true,
            "type": "text"
        }
    ]
}
```


扩展开发完成后，将`my_extension`文件夹，上传到`src/plugins`文件夹中。或者使用web界面进行上传。
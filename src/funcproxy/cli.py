import click
from .core.server import start_server

@click.command()
@click.option("--port", default=7777, help="HTTP server port")
@click.option("--debug/--no-debug", default=False, help="是否开启调试模式")
def main(port: int, debug: bool, plugin_dir: str = "plugins"):
    """启动 HTTP 服务器并加载插件"""
    start_server(port=port, plugin_dir=plugin_dir, debug=debug)

if __name__ == "__main__":
    main()
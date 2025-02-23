import click
from .core.server import start_server

@click.command()
@click.option("--port", default=7777, help="HTTP server port")
@click.option("--debug/--no-debug", default=False, help="debug mode")
def main(port: int, debug: bool):
    """启动 HTTP 服务器并加载插件"""
    bannar = r'''
     _____                 ____                      
    |  ___|   _ _ __   ___|  _ \ _ __ _____  ___   _ 
    | |_ | | | | '_ \ / __| |_) | '__/ _ \ \/ / | | |
    |  _|| |_| | | | | (__|  __/| | | (_) >  <| |_| |
    |_|   \__,_|_| |_|\___|_|   |_|  \___/_/\_\\__, |
                                                |___/ 
    '''
    print(bannar)
    start_server(port=port, debug=debug)

if __name__ == "__main__":
    main()
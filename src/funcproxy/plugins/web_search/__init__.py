from funcproxy.core.plugin_base import PluginBase
import json
import requests

class Plugin(PluginBase):
    def __init__(self):
        self.logger.info("Web Search Plugin initialized")
        self.firecrawl_api = "https://api.firecrawl.dev/v1/scrape"
        self.tavily_api = "https://api.tavily.com/search"

    def do_search_online(self, parameters) -> str:
        parameters = json.loads(parameters)
        setting = self.get_settings()
        try:
            headers = {
                "Authorization": "Bearer " + setting["tavily_apikey"],
                "Content-Type": "application/json"
            }
            data = {
                "query": str(parameters["keyword"])
            }
            self.logger.debug("tavily data: %s", data)
            response = requests.post(self.tavily_api, headers=headers, json=data)
            if response.status_code == 200:
                return str(response.json())
            return "not found"
        except Exception as e:
            self.logger.error("Error: %s", e)
            return "Search tool is abnormal"
    
    def do_open_website(self, parameters) -> str:
        parameters = json.loads(parameters)
        setting = self.get_settings()
        try:
            headers = {
                "Authorization": "Bearer " + setting["firecrawl_apikey"]
            }
            data = {
                "url": parameters["url"],
                "formats": ["markdown"]
            }
            response = requests.post(self.firecrawl_api, json=data, headers=headers)
            if response.status_code == 200:
                if response.json()['success'] == True:
                    return response.json()["data"]["markdown"]
            return "not found"
        except Exception as e:
            self.logger.error(e)
            return "not found"
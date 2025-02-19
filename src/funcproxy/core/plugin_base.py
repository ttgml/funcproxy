

class PluginBase:
    def name(self) -> str:
        """
        The name of the plugin.
        """
        raise NotImplementedError("PluginBase.name is not implemented")
    

    def id(self) -> str:
        """
        The id of the plugin.
        """
        raise NotImplementedError("PluginBase.id is not implemented")
    
    def function_call(self, parameters: dict) -> dict:
        """
        Called when a function call is made.
        """
        raise NotImplementedError("PluginBase.function_call is not implemented")
    
    def add_function(self, tools: list) -> list:
        """
        Add a function to the plugin.
        """
        raise NotImplementedError("PluginBase.add_function is not implemented")
    
    def install(self, config: dict) -> dict:
        """
        Install the plugin.
        """
        raise NotImplementedError("PluginBase.install is not implemented")
    
    def uninstall(self, config: dict) -> dict:
        """
        Uninstall the plugin.
        """
        raise NotImplementedError("PluginBase.uninstall is not implemented")
    
    def enable(self, config: dict) -> dict:
        """
        Enable the plugin.
        """
        raise NotImplementedError("PluginBase.enable is not implemented")
    
    def disable(self, config: dict) -> dict:
        """
        Disable the plugin.
        """
        raise NotImplementedError("PluginBase.disable is not implemented")
    

class SnowGraphConnection:
    HOST: str = None
    PORT: int = None

    def set_host(self, host):
        self.HOST = host
        return self

    def set_port(self, port):
        self.PORT = port
        return self

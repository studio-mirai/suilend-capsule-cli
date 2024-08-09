from pysui import SuiConfig, SyncClient


class Sui:
    def __init__(self) -> None:
        self.config = SuiConfig.default_config()
        self.client = SyncClient(self.config)

from pathlib import Path

from isimip_utils.config import ISIMIPSettings
from isimip_utils.decorators import cached_property
from isimip_utils.fetch import (fetch_definitions, fetch_pattern,
                                fetch_schema, fetch_tree)


class Settings(ISIMIPSettings):

    def setup(self, parser):
        super().setup(parser)
        self.DATASET_PATH = Path(settings.DATASET_PATH)
        self.PROTOCOL_PATH = Path(*self.DATASET_PATH.parts[:3])

    @cached_property
    def DEFINITIONS(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_definitions(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def PATTERN(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_pattern(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def SCHEMA(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_schema(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)

    @cached_property
    def TREE(self):
        assert self.PROTOCOL_LOCATIONS is not None, 'PROTOCOL_LOCATIONS is not set'
        return fetch_tree(self.PROTOCOL_LOCATIONS.split(), self.PROTOCOL_PATH)


settings = Settings()

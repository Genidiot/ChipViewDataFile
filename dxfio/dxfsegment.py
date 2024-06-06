from ezdxf.entities import Polyline
from typing import cast
from ezdxf.document import Drawing


class DxfSegment:
    def __init__(self, dwg: Drawing):
        self.dwg = dwg

    def get_blocks_entities(self):
        entities = dict()
        for block in self.dwg.blocks:
            for entity in block:
                if entity.dxftype() == "POLYLINE":
                    entities[block.name] = cast("Polyline", entity)
        return entities

    def add_entity(self, blockname, entity):
        block = self.dwg.blocks.new(blockname, {0, 0, 0})
        block.add_entity(entity)

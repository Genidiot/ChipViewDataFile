from typing import cast
from ezdxf.document import Drawing


class DxfBlock:
    def __init__(self, dwg: Drawing):
        self.dwg = dwg
        self.__create_attrib_template()

    def get_specific_blocks(self, block_name: str) -> list:
        block_list = []
        for e in self.dwg.blocks:
            if e.name == block_name:
                block_list.append(e.block)
        return block_list

    def get_blocks_name(self) -> list:
        block_name_list = []
        for e in self.dwg.blocks:
            if e.name != "*Model_Space" and e.name != "*Paper_Space":
                block_name_list.append(e.name)
        return block_name_list

    def __create_attrib_template(self):
        for e in self.dwg.blocks:
            e.add_attdef(tag="NAME", insert=(0.5, -0.5), dxfattribs={"height": 0.5, "color": 3})
            e.add_attdef(tag="XPOS", insert=(0.5, -1.0), dxfattribs={"height": 0.5, "color": 3})
            e.add_attdef(tag="YPOS", insert=(0.5, -1.5), dxfattribs={"height": 0.5, "color": 3})

    def get_sub_block_ref(self):
        blockreflist = []
        for e in self.dwg.blocks:
            for entity in e:
                if entity.dxftype() == "INSERT":
                    blockref = cast("Insert", entity)
                    blockreflist.append(
                        {
                            "Block Name": blockref.dxf.name,
                            "Insertion Point": blockref.dxf.insert,
                            "Rotation Angle": blockref.dxf.rotation
                         }
                    )
        return blockreflist

import os
from dxfio import dxfblock
from dxfio import dxfreader


class DxfBlocks:
    def __init__(self, path: str):
        self.path = path
        self.dwg_list = list()
        self.blocks_name_list = list()
        self.sub_block_ref = list()
        self.read_all_file()

    def find_all_file(self):
        for root, ds, fs in os.walk(self.path):
            for f in fs:
                if f.endswith(".dxf"):
                    fullname = os.path.join(root, f)
                    yield fullname

    def read_all_file(self):
        for filename in self.find_all_file():
            dxf = dxfreader.DxfReader(filename)
            block = dxfblock.DxfBlock(dxf.get_dwg())
            self.dwg_list.append(dxf.get_dwg())
            self.blocks_name_list += block.get_blocks_name()
            self.sub_block_ref += block.get_sub_block_ref()

    def get_blocks_name(self) -> dict:
        return self.blocks_name_list

    def get_dwgs(self) -> list:
        return self.dwg_list

    def get_sub_blocks_ref(self):
        return self.sub_block_ref


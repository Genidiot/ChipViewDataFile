# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os

import ezdxf
import chipviewconfig
from dxfio import dxfblocks
from dxfio import dxfchipview


def test_create_block():
    doc = ezdxf.new("R2010")
    flag = doc.blocks.new(name="Flag", base_point=(100, 100, 0))
    flag.add_lwpolyline([(0, 0), (0, 5), (4, 3), (0, 3)])
    flag.add_circle((0, 0), .4, dxfattribs= {'color': 2})
    doc.saveas("./testblock1.dxf")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config = chipviewconfig.ChipViewConfig(f"./config/test2.json")

    dxf_chip_view = dxfchipview.DxfChipView(config)

    blocks = dxfblocks.DxfBlocks(f"./dxf/test_import")
    blockspins = blocks.get_sub_blocks_ref()
    block_dwg = blocks.get_dwgs()
    blocksname = list(set(config.get_type_names()) & set(list(blocks.get_blocks_name())))
    dxf_chip_view.import_block(block_dwg)
    dxf_chip_view.add_CLCM_refs()

    # segments = dxfblocks.DxfBlocks(f"./dxf/TC2/segment")
    # segment_dwg = segments.get_dwgs()
    # dxf_chip_view.import_block(segment_dwg)
    #
    # dxf_chip_view.add_block_refs()
    # dxf_chip_view.add_swh_segment_refs(blocksname, blockspins, segments.get_blocks_name())
    dxf_chip_view.save_as(f"./result/testCLCL.dxf")

    #test_create_block()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import ezdxf
from ezdxf.addons import Importer
from ezdxf.entities import Polyline, LWPolyline
from ezdxf.entities import Line

from typing import cast

from ezdxf.math import UVec

import chipviewconfig
from chipviewconfig import LineOffset
from chipviewconfig import LogicPoint


def get_segment_lenght(segmentname: str):
    if segmentname[2:4]=="12":
        return 12
    elif segmentname[2:3]=="2":
        return 2
    # elif segmentname.find("L3") != -1:
    #     return 3
    elif segmentname[2:3]=="4":
        return 4
    elif segmentname[2:3]=="6":
        return 6
    elif segmentname[2:3]=="1":
        return 1
    elif segmentname[0:4]=="POST":
        return 0.5
    else:
        return -1
    # if segmentname.find("L14") != -1:
    #     return 14
    # elif segmentname.find("L2") != -1:
    #     return 2
    # elif segmentname.find("L3") != -1:
    #     return 3
    # elif segmentname.find("L4") != -1:
    #     return 4
    # elif segmentname.find("L6") != -1:
    #     return 6
    # elif segmentname.find("L1") != -1:
    #     return 1
    # else:
    #     return -1


def extend_segment_lenght(segment: LWPolyline, direction: str, breakindexlist : list, offsetdict: dict):
    newpolyline = LWPolyline()
    vecsourcepoints = segment.get_points()
    vecdestpoints = list()
    i = 0
    for breakindex in breakindexlist:
        number = 0
        for point in vecsourcepoints:
            if number >= (breakindex + 1) * 2:
                if direction == "EE":
                    x = point[0] + offsetdict[breakindex]
                    y = point[1]
                elif direction == "WW":
                    x = point[0] - offsetdict[breakindex]
                    y = point[1]
                elif direction == "NN":
                    x = point[0]
                    y = point[1] + offsetdict[breakindex]
                else:
                    x = point[0]
                    y = point[1] - offsetdict[breakindex]
            else:
                x = point[0]
                y = point[1]
            vecdestpoints.append((x, y, point[2], point[3], point[4]))
            number += 1

        vecsourcepoints.clear()
        vecsourcepoints = vecdestpoints
        if i != len(breakindexlist) - 1:
            vecdestpoints.clear()
        i += 1
    newpolyline.append_points(vecdestpoints)

    return newpolyline


class DxfChipView:
    def __init__(self, config: chipviewconfig.ChipViewConfig):
        self.dwg = ezdxf.new(dxfversion='AC1021')
        ezdxf.setup_linetypes(self.dwg)
        self.msp = self.dwg.modelspace()
        self.config = config

    def get_dwg(self):
        return self.dwg

    def get_msp(self):
        return self.msp

    def add_entity(self, entity):
        self.msp.add_entity(entity)

    def get_blocks_name(self, dwg) -> list:
        block_name_list = []
        for e in dwg.blocks:
            if e.name != "*Model_Space" and e.name != "*Paper_Space":
                block_name_list.append(e.name)
        return block_name_list

    def query_block_ref(self, blockrefname: str):
        return self.msp.query('INSERT[name==%s]' % blockrefname)

    def import_block(self, sourcedwgs: list):
        for dwg in sourcedwgs:
            importer = Importer(dwg, self.dwg)
            importer.import_blocks(self.get_blocks_name(dwg))
            importer.finalize()

    def add_CLCM_refs(self):
        block_ref = self.msp.add_blockref("CLCM", (0, 0))

    def add_block_refs(self):
        for item_regions in self.config.get_items_region():
            for region in item_regions.get_regions():
                for point in region.get_logic_points():
                    values = {
                        "ItemType": item_regions.get_item_type(),
                        "XPOS": "X = %d" % point.get_column(),
                        "YPOS": "Y = %d" % point.get_row()
                    }
                    block_ref = self.msp.add_blockref(
                        item_regions.get_item_type(),
                        (
                            point.get_column() * self.config.get_columns_width(),
                            point.get_row() * self.config.get_rows_height()
                        )
                    )
                   # block_ref.add_auto_attribs(values)

    def add_swh_segment_refs(self, blocksname: list, pins: list, segmentsname: list):
        for entity in self.msp:
            if entity.dxftype() == 'INSERT':
                blockref = cast("Insert", entity)
                if blockref.dxf.name != "SWH" or blocksname.count(blockref.dxf.name) == 0:
                    continue
                logiccolumn: int = int(blockref.dxf.insert[0] / self.config.get_columns_width())
                logicrow: int = int(blockref.dxf.insert[1] / self.config.get_rows_height())
                for segment in segmentsname:
                    terms = segment.split("-")
                    if len(terms) == 2:
                        startterm: str = terms[0]
                        pinpoint = self.get_block_pin_point(startterm, pins)
                        if pinpoint is not None:
                            segmentrefsname = self.get_segment_ref_name(logiccolumn, logicrow, segment)
                            if segmentrefsname is not None:
                                self.msp.add_blockref(segmentrefsname, blockref.dxf.insert + pinpoint)
                    elif len(terms) == 3:
                        if terms[2] == "N" or terms[2] == "S":
                            startterm: str = terms[0]
                            pinpoint = self.get_block_pin_point(startterm, pins)
                            if pinpoint is not None:
                                segmentrefsname = self.get_directLine_ref_name(logicrow, segment)
                                if segmentrefsname is not None:
                                    self.msp.add_blockref(segmentrefsname, blockref.dxf.insert + pinpoint)

    def get_block_ref(self):
        for entity in self.msp:
            print(entity.dxftype())
            if entity.dxftype() == 'INSERT':
                blockref = cast("Insert", entity)
                print(f"Block Name: {blockref.dxf.name}")
                print(f"Insertion Point: {blockref.dxf.insert}")
                print(f"Rotation Angle: {blockref.dxf.rotation}")

    def get_segment_ref_name(self, startcolumn, startrow, segmentname: str):
        terms = segmentname.split("-")
        if len(terms) != 2:
            return segmentname
        startterm: str = terms[0]
        endterm: str = terms[1]
        segmentlength = get_segment_lenght(startterm)
        if segmentlength == -1:
            return segmentname

        if startterm.startswith("EE"):
            endcolumn = startcolumn + segmentlength * 2
            endrow = startrow
            if endcolumn > self.config.get_column_count():
                # Line crossing the boundary
                index: int = int(segmentlength - (endcolumn - self.config.get_column_count()) / 2)
                segmentname = startterm + "-" + endterm.replace("EE", "WW") + "-" + str(index)
            else:
                #Lines that need to be expanded
                linesoffset = self.config.lines_need_offset(LogicPoint(startrow, startcolumn),
                                                            LogicPoint(endrow, endcolumn))
                if len(linesoffset) == 0:
                    return segmentname

                newsegmentname: str = segmentname
                breakindexlist = list()
                offsetdic = dict()
                for offs in linesoffset:
                    if offs.directiontype == 1:
                        breakindex = int((offs.index - startcolumn) / 2 - 1)
                        newsegmentname += "-extend_" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                    elif offs.directiontype == "EEshorten":
                        breakindex = int((offs.index - startcolumn) / 2)
                        newsegmentname += "-shorten_" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                self.add_extend_segment_to_block(segmentname, newsegmentname, "EE", breakindexlist, offsetdic)
                segmentname = newsegmentname
        elif startterm.startswith("WW"):
            endcolumn = startcolumn - segmentlength * 2 - 1
            endrow = startrow
            if endcolumn < 0:
                index: int = int(segmentlength - (0 - endcolumn) / 2)
                segmentname = startterm + "-" + endterm.replace("WW", "EE") + "-" + str(index)
            else:
                #Lines that need to be expanded
                endcolumn = startcolumn - segmentlength * 2
                linesoffset = self.config.lines_need_offset(LogicPoint(startrow, startcolumn),
                                                            LogicPoint(endrow, endcolumn))
                if len(linesoffset) == 0:
                    return segmentname

                breakindexlist = list()
                offsetdic = dict()
                newsegmentname: str = segmentname
                for offs in linesoffset:
                    if offs.directiontype == 1:
                        breakindex = int((startcolumn - offs.index) / 2)
                        newsegmentname += "-extend_" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                    elif offs.directiontype == "WWshorten":
                        breakindex = int((startcolumn - offs.index) / 2)
                        newsegmentname += "-shorten_" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                self.add_extend_segment_to_block(segmentname, newsegmentname, "WW", breakindexlist, offsetdic)
                segmentname = newsegmentname
        elif startterm.startswith("NN"):
            endcolumn = startcolumn
            endrow = startrow + segmentlength
            if endrow > self.config.get_row_count():
                index: int = int(segmentlength - (endrow - self.config.get_row_count()))
                segmentname = startterm + "-" + endterm.replace("NN", "SS") + "-" + str(index)
            else:
                #Lines that need to be expanded
                linesoffset = self.config.lines_need_offset(LogicPoint(startrow, startcolumn),
                                                            LogicPoint(endrow, endcolumn))
                if len(linesoffset) == 0:
                    return segmentname

                breakindexlist = list()
                offsetdic = dict()
                newsegmentname: str = segmentname
                for offs in linesoffset:
                    if offs.directiontype == 0:
                        breakindex = int((offs.index - startrow) - 1)
                        newsegmentname += "-extend_" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                    elif offs.directiontype == "NNextend":
                        breakindex = int((offs.index - startrow) - 1)
                        newsegmentname += "-doubleextend" + str(breakindex)
                        breakindexlist.append(breakindex)
                        offsetdic[breakindex] = offs.offset
                self.add_extend_segment_to_block(segmentname, newsegmentname, "NN", breakindexlist, offsetdic)
                segmentname = newsegmentname
        elif startterm.startswith("SS"):
            endcolumn = startcolumn
            endrow = startrow - segmentlength
            if endrow < 0:
                index: int = int(segmentlength - (0 - endrow))
                segmentname = startterm + "-" + endterm.replace("SS", "NN") + "-" + str(index)
            else:
                #Lines that need to be expanded
                linesoffset = self.config.lines_need_offset(LogicPoint(startrow, startcolumn),
                                                            LogicPoint(endrow, endcolumn))
                if len(linesoffset) == 0:
                    return segmentname

                breakindexlist = list()
                offsetdic = dict()
                newsegmentname: str = segmentname
                for offs in linesoffset:
                    if offs.directiontype != 0:
                        continue
                    breakindex = int((startrow - offs.index) - 1)
                    newsegmentname += "-extend_" + str(breakindex)
                    breakindexlist.append(breakindex)
                    offsetdic[breakindex] = offs.offset

                self.add_extend_segment_to_block(segmentname, newsegmentname, "SS", breakindexlist, offsetdic)
                segmentname = newsegmentname
        else:
            raise Exception("The name of the line segment does not comply with the rules!")

        return segmentname

    def get_directLine_ref_name(self, startrow, segmentname: str):
        terms = segmentname.split("-")
        if len(terms) != 3:
            return segmentname
        if startrow == 0 and terms[2] == "S":
            return None
        elif startrow == self.config.get_row_count() and terms[2] == "N":
            return None

        for offset in self.config.get_lines_offset():
            if offset.directiontype == 0:
                if startrow == offset.index + 1 and terms[2] == "S":
                    newsegmentname: str = segmentname
                    newsegmentname += "-extend"
                    if self.dwg.blocks.get(newsegmentname) is None:
                        newLineblock = self.dwg.blocks.new(name=newsegmentname)
                        newLineblock.add_line((0, 0), (0, -1000-offset.offset))
                        return newsegmentname
                    else:
                        return newsegmentname
                elif startrow == offset.index - 1 and terms[2] == "N":
                    newsegmentname: str = segmentname
                    newsegmentname += "-extend"
                    if self.dwg.blocks.get(newsegmentname) is None:
                        newLineblock = self.dwg.blocks.new(name=newsegmentname)
                        newLineblock.add_line((0, 0), (0, 1000 + offset.offset))
                        return newsegmentname
                    else:
                        return newsegmentname
        return segmentname

    def get_block_pin_point(self, pinname, pins: list):
        for pin in pins:
            if pin["Block Name"] == pinname:
                return pin["Insertion Point"]

    def get_blocks_entities(self, blockname):
        block = self.dwg.blocks.get(blockname)
        if block is None:
            return None

        for entity in block:
            if entity.dxftype() == "LWPOLYLINE":
                return cast("LWPolyline", entity)
            elif entity.dxftype() == "LINE":
                return cast("LINE", entity)

        return None

    def add_entity_to_block(self, blockname, entity):
        block = self.dwg.blocks.new(blockname)
        block.add_entity(entity)

    def add_extend_segment_to_block(self, blockname: str, newblockname: str, direction: str, breakindexlist: list, offsetdict: dict):
        if self.dwg.blocks.get(newblockname) is not None:
            return

        entity = self.get_blocks_entities(blockname)
        if entity is None:
            return

        extendentity = extend_segment_lenght(entity, direction, breakindexlist, offsetdict)
        if extendentity is not None:
            self.add_entity_to_block(newblockname, extendentity)

    def save_as(self, filename: str):
        self.dwg.saveas(filename=filename)

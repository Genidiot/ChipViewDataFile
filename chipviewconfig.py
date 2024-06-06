import json

UNIT_WIDTH = 10
UNIT_HEIGHT = 10


class LogicPoint:
    def __init__(self, row=0, column=0):
        self.row = row
        self.column = column

    def __eq__(self, other):
        if isinstance(self, other):
            return self.row == other.row and self.column == other.column
        return False

    def set_row(self, row):
        self.row = row

    def set_column(self, column):
        self.column = column

    def get_row(self):
        return self.row

    def get_column(self):
        return self.column


class LogicRegion:
    def __init__(self, point_start=LogicPoint(), point_end=LogicPoint(), item_width=10, item_height=10):
        self.point_start = point_start
        self.point_end = point_end
        self.item_width = item_width
        self.item_height = item_height

    def set_point_start(self, point_start: LogicPoint):
        self.point_start = point_start

    def set_point_end(self, point_end: LogicPoint):
        self.point_end = point_end

    def __min_row(self):
        return min(self.point_start.get_row(), self.point_end.get_row())

    def __min_column(self):
        return min(self.point_start.get_column(), self.point_end.get_column())

    def __max_row(self):
        return max(self.point_start.get_row(), self.point_end.get_row())

    def __max_column(self):
        return max(self.point_start.get_column(), self.point_end.get_column())

    def is_row_in_region(self, row):
        if self.__min_row() <= row <= self.__max_row():
            return True
        else:
            return False

    def is_column_in_region(self, column):
        if self.__min_column() <= column <= self.__max_column():
            return True
        else:
            return False

    def is_column_in_region2(self, column):
        if self.__min_column() <= column < self.__max_column():
            return True
        else:
            return False

    def is_column_in_region3(self, column):
        if self.__min_column() < column <= self.__max_column():
            return True
        else:
            return False

    def get_logic_points(self) -> list:
        point_list = []
        row = self.__min_row()
        while row < self.__max_row() + 1:
            column = self.__min_column()
            while column < self.__max_column() + 1:
                point_list.append(LogicPoint(row, column))
                column += self.item_width / UNIT_WIDTH
            row += self.item_height / UNIT_HEIGHT
        return point_list


class ItemRegions:
    def __init__(self, item_type="", item_width=10, item_height=10):
        self.item_type = item_type
        self.item_width = item_width
        self.item_height = item_height
        self.regions = []

    def add_region(self, region: LogicRegion):
        self.regions.append(region)

    def set_regions(self, region_list: list):
        self.regions = region_list

    def get_regions(self):
        return self.regions

    def set_item_type(self, item_type: str):
        self.item_type = item_type

    def get_item_type(self):
        return self.item_type

    def set_item_type(self, item_width):
        self.item_width = item_width

    def get_item_width(self):
        return self.item_width

    def set_item_height(self, item_height):
        self.item_height = item_height

    def get_item_height(self):
        return self.item_height


class LineOffset:
    def __init__(self, directiontype=0, index=0, offset=0):
        self.directiontype = directiontype
        self.index = index
        self.offset = offset


class ChipViewConfig:
    def __init__(self, filename):
        self.filename = filename
        self.name = ""
        self.row_count = 0
        self.column_count = 0
        self.columns_width = 0
        self.rows_height = 0
        self.lines_offset = list()
        self.items_region = list()

        self.__read_config()

    def __read_config(self):
        with open(self.filename, 'r') as configfile:
            configuration = json.load(configfile)
        self.__parser_config(configuration)

    def __parser_config(self, configuration: dict):
        self.name = configuration["name"]
        self.row_count = configuration["rowCount"] - 1
        self.column_count = configuration["columnCount"] - 1
        self.columns_width = configuration["columnWidth"]
        self.rows_height = configuration["rowHeight"]

        for lineoffset in configuration["lineOffset"]:
            templineoffset = LineOffset(lineoffset["directionType"], lineoffset["index"], lineoffset["offset"])
            self.lines_offset.append(templineoffset)

        for item_region in configuration["itemRegions"]:
            item_regions = ItemRegions(item_region["itemType"], item_region["itemWidth"], item_region["itemHeight"])
            for region in item_region["regions"]:
                point_start = LogicPoint(region["positionStart"]["row"], region["positionStart"]["column"])
                point_end = LogicPoint(region["positionEnd"]["row"], region["positionEnd"]["column"])
                item_regions.add_region(LogicRegion(point_start, point_end, item_region["itemWidth"], item_region["itemHeight"]))
            self.items_region.append(item_regions)

    def lines_need_offset(self, startpoint: LogicPoint, endpoint: LogicPoint):
        linesoffset = list()
        logic_region = LogicRegion(startpoint, endpoint)
        for offset in self.lines_offset:
            if offset.directiontype == 0 and logic_region.is_row_in_region(offset.index):
                linesoffset.append(offset)
            elif offset.directiontype == 1 and logic_region.is_column_in_region(offset.index):
                linesoffset.append(offset)
            elif offset.directiontype == "EEshorten" and logic_region.is_column_in_region2(offset.index):
                linesoffset.append(offset)
            elif offset.directiontype == "WWshorten" and logic_region.is_column_in_region3(offset.index):
                linesoffset.append(offset)
            elif offset.directiontype == "NNextend" and logic_region.is_row_in_region(offset.index):
                linesoffset.append(offset)
            else:
                pass
        return linesoffset

    def get_config_name(self):
        return self.name

    def get_row_count(self):
        return self.row_count

    def get_column_count(self):
        return self.column_count

    def get_columns_width(self):
        return self.columns_width

    def get_rows_height(self):
        return self.rows_height

    def get_items_region(self):
        return self.items_region

    def get_lines_offset(self):
        return self.lines_offset

    def get_type_names(self):
        typenames = list()
        for items_region in self.items_region:
            typenames.append(items_region.get_item_type())
        return typenames

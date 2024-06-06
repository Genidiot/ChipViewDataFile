import ezdxf
from ezdxf import recover


class DxfReader:
    def __init__(self, filename: str):
        self.filename = filename
        self.dwg = self.read_dxf()
        self.msp = self.dwg.modelspace()

    def set_filename(self, filename: str):
        self.filename = filename

    def read_dxf(self):
        try:
            doc = ezdxf.readfile(self.filename)
        except IOError:
            print(f"Not a DXF file or a generic I/O error.")
        except ezdxf.DXFStructureError:
            doc = self.read_dxf_recover()

        return doc

    def read_dxf_recover(self):
        try:
            doc, auditor = recover.readfile(self.filename)
        except IOError:
            print(f"Not a DXF file or a generic I/O error.")
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file: {self.filename}.")

        if auditor.has_errors:
            print(f"Found unrecoverable errors in DXF file: {self.filename}.")
            auditor.print_error_report()

        return doc

    def get_dwg(self):
        return self.dwg

import ezdxf
from converter import entity_to_gcode

filename = "DXF_from_inventor_test.dxf"
doc = ezdxf.readfile("drawings/" + filename)
msp = doc.modelspace()

gcode = [
    "G21",      # mm
    "G90",      # absolute positioning
    "M5",       # pen up
]

for e in msp:
    gcode += entity_to_gcode(e)

gcode.append("M2")

with open(f"generatedGcode/{filename.replace('.dxf', '.gcode')}", "w") as f:
    f.write("\n".join(gcode))

print("Wrote output.gcode")
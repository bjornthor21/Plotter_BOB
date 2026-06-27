import ezdxf

doc = ezdxf.readfile("DXF_from_inventor_test.dxf")

print("DXF version:", doc.dxfversion)

types = []
for e in doc.modelspace():
    #if e.dxftype() == "ACAD_PROXY_ENTITY":
        #print(e.dxfattribs())
    if e.dxftype() not in types:
        types.append(e.dxftype())

print("Entity types found:", types)
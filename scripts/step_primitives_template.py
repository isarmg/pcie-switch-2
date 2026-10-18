"""Write a closed polyhedral STEP B-rep; validate all shell edges before export."""
from pathlib import Path
from collections import Counter
import math,json
R=Path(__file__).resolve().parents[1];O=R/'outputs/E1S_12slot_10mm'
def ring(x,y,z,cx=0):return [(cx-x,-y,z),(cx+x,-y,z),(cx+x,y,z),(cx-x,y,z)]
# SFF-TA-1006 Rev 2.0 Fig 5-1/Table 5-1: Datum E is 11.23 mm
# from the card edge. The 31.5 mm body center is 4.52 mm from E.
# Fig 6-1: contact A1 is -8.015 mm from E. Samtec PCB A1 is
# -7.995 mm from this footprint origin, hence E = +0.020 mm.
datum_e=.020
body_center=datum_e+(31.5/2-11.23)
assert abs(body_center-4.54)<1e-10
top=ring(15.75,2.95,117.49,body_center);bottom=ring(15.75,2.95,12,body_center)
# 18.48 mm mating card width; C2=6 mm minimum exposed tongue length.
necktop=ring(9.24,.785,12,datum_e);neckbottom=ring(9.24,.785,6,datum_e)
faces=[top,neckbottom[::-1]]
for i in range(4):
    n=(i+1)%4
    faces.append([bottom[i],bottom[n],top[n],top[i]])
    faces.append([neckbottom[i],neckbottom[n],necktop[n],necktop[i]])
    faces.append([bottom[n],bottom[i],necktop[i],necktop[n]])
directed=Counter((a,b) for face in faces for a,b in zip(face,face[1:]+face[:1]))
assert all(count==1 and directed[(b,a)]==1 for (a,b),count in directed.items())
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(v):
    l=math.sqrt(sum(x*x for x in v));return tuple(x/l for x in v)
volume=0
for f in faces:
    for i in range(1,len(f)-1):volume+=sum(a*b for a,b in zip(f[0],cross(f[i],f[i+1])))/6
assert abs(volume-(31.5*5.9*105.49+18.48*1.57*6))<1e-6
entities=[]
def add(s):entities.append(f'#{len(entities)+1} = {s};');return '#'+str(len(entities))
def nums(v):return '('+','.join(f'{x:.9f}' for x in v)+')'
def refs(v):return '('+','.join(v)+')'
ctx=add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{ctx})")
pc=add(f"PRODUCT_CONTEXT('',{ctx},'mechanical')")
prod=add(f"PRODUCT('E1S 5.9mm SSD simplified','E1S 5.9mm SSD simplified','Assumed insertion depth; not manufacturer CAD',({pc}))")
form=add(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
pdc=add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{ctx},'design')")
pd=add(f"PRODUCT_DEFINITION('design','',{form},{pdc})")
pds=add(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
lu=add('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')
au=add('(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))')
su=add('(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())')
unc=add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-7),{lu},'distance_accuracy_value','')")
rc=add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu},{au},{su})) REPRESENTATION_CONTEXT('','3D'))")
points={v:add("CARTESIAN_POINT('',"+nums(v)+')') for v in sorted(set(sum(faces,[])))}
faceids=[]
for f in faces:
    a=sub(f[1],f[0]);b=sub(f[2],f[1]);normal=unit(cross(a,b))
    loop=add(f"POLY_LOOP('',{refs([points[v] for v in f])})")
    bound=add(f"FACE_OUTER_BOUND('',{loop},.T.)")
    dn=add("DIRECTION('',"+nums(normal)+')');dx=add("DIRECTION('',"+nums(unit(a))+')')
    ax=add(f"AXIS2_PLACEMENT_3D('',{points[f[0]]},{dn},{dx})")
    plane=add(f"PLANE('',{ax})")
    faceids.append(add(f"FACE_SURFACE('',({bound}),{plane},.T.)"))
shell=add(f"CLOSED_SHELL('',{refs(faceids)})")
solid=add(f"FACETED_BREP('E1S SSD closed solid',{shell})")
representation=add(f"FACETED_BREP_SHAPE_REPRESENTATION('',({solid}),{rc})")
add(f'SHAPE_DEFINITION_REPRESENTATION({pds},{representation})')
color=add("COLOUR_RGB('',0.55,0.67,0.78)")
fillcolor=add(f"FILL_AREA_STYLE_COLOUR('',{color})")
fill=add(f"FILL_AREA_STYLE('',({fillcolor}))")
surfacefill=add(f'SURFACE_STYLE_FILL_AREA({fill})')
side=add(f"SURFACE_SIDE_STYLE('',({surfacefill}))")
style=add(f'SURFACE_STYLE_USAGE(.BOTH.,{side})')
assignment=add(f'PRESENTATION_STYLE_ASSIGNMENT(({style}))')
styled=add(f"STYLED_ITEM('',({assignment}),{solid})")
add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({styled}),{rc})")
header="ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Closed SSD envelope'),'2;1');\nFILE_NAME('E1S_5p9_simplified.step','2026-09-25T12:00:00',(''),(''),'STEP writer','STEP writer','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"
(O/'models/E1S_5p9_simplified.step').write_text(header+'\n'.join(entities)+'\nENDSEC;\nEND-ISO-10303-21;\n',encoding='ascii')
geometry={'faces':len(faces),'closed_shell_edges':len(directed)//2,'signed_volume_mm3':volume,'envelope_mm':[31.5,5.9,111.49],'datum_e_from_card_edge_mm':11.23,'body_center_from_datum_e_mm':4.52,'body_center_from_footprint_origin_mm':4.54,'datum_e_from_footprint_origin_mm':.02,'tongue_width_mm':18.48,'tongue_length_mm':6,'body_edge_x_mm':[-11.21,20.29],'a1_from_card_edge_mm':3.215,'source':'SFF-TA-1006 Rev 2.0 Fig 5-1, Table 5-1, Fig 6-1; Samtec footprint Rev E'}
(O/'SSD_GEOMETRY.json').write_text(json.dumps(geometry,indent=2),encoding='utf8')
print(json.dumps(geometry))

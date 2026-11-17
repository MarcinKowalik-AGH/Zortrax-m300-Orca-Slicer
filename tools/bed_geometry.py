#!/usr/bin/env python3
"""Measured 360 mm M300 Classic visual bed mesh for Orca, generated locally.

This deliberately does NOT change the slicer's 300 x 305 mm printable polygon.
Model origin is the Orca print-volume centre (150, 152.5); the physical plate's
geometric centre is (150,150) in printer coordinates. The 2.5 mm Y displacement
is intentional. Orca translates the STL by the print-volume centre.
Only the NON-printable outer margin is meshed; the vector texture already
supplies the perforated interior and five gold contact pads.
"""
from functools import lru_cache
from io import BytesIO
from math import cos, sin, hypot, pi, sqrt
from struct import pack

PHYSICAL_MM = (360.0, 360.0)
PRINTABLE_MM = (300.0, 305.0)
PRINTABLE_PHYSICAL_BOUNDS_MM = (30.0, 330.0, 30.0, 335.0)
PERFORATED_PHYSICAL_BOUNDS_MM = (14.0, 346.0, 15.0, 344.0)
PAD_CORNER_MM = (60.0, 60.0)
PAD_CENTRE_MM = (50.0, 50.0)
# Reference: rectified OEM platform photo + user close-up IMG_9059/9063.
# There are FIVE countersunk Allen screws on each frame edge including corners,
# hence 16 unique bolts total (5+5+3+3). The previous 17 mm offsets were
# incorrect: these heads are on the narrow outer metal flange, ~6 mm from
# the physical 360 mm sheet edge. Intermediate pitch is approximately 87 mm.
# Dimensions are photo-derived estimates; no caliper survey of fastener centres.
FRAME_SCREW_EDGE_MM = (6.0, 93.0, 180.0, 267.0, 354.0)
FRAME_SCREWS = (
    tuple((x, y) for x in FRAME_SCREW_EDGE_MM for y in (6.0,354.0)) +
    tuple((x, y) for y in FRAME_SCREW_EDGE_MM[1:-1] for x in (6.0,354.0))
)
assert len(set(FRAME_SCREWS)) == 16
# Align the visible top of the STL with Orca's printable-plane overlay:
# Bed3D moves model coordinates by approximately -0.41 mm in Z.
PLATE_THICKNESS_MM = 3.0
TOP_Z = .41
BOTTOM_Z = TOP_Z - PLATE_THICKNESS_MM
PERFORATION_PITCH_MM = 3.0
PERFORATION_RADIUS_MM = .76

# Reference: operator's ruler photographs IMG_9060, IMG_9061, IMG_9062,
# IMG_9063 and close-up IMG_9058. Dimensions/position are approximate
# photographic estimates, NOT caliper measurements.
# x is measured from the LEFT of the 360 mm physical plate (front-left origin).
# Connector visibly straddles the rear y=360 edge by only about 1-2 mm.
REAR_CONNECTOR_CENTER_X_MM = 148.0
REAR_CONNECTOR_SHELL_WIDTH_MM = 8.5
REAR_CONNECTOR_TOTAL_WIDTH_MM = 12.0
REAR_CONNECTOR_PROTRUSION_MM = 1.6
REAR_CONNECTOR_INBOARD_MM = 5.4
REAR_CONNECTOR_BODY_HEIGHT_MM = 3.2  # provisional, not measured
REAR_CONNECTOR_SHELL_BOUNDS_MM = (
    REAR_CONNECTOR_CENTER_X_MM - REAR_CONNECTOR_SHELL_WIDTH_MM / 2,
    360.0 - REAR_CONNECTOR_INBOARD_MM,
    REAR_CONNECTOR_CENTER_X_MM + REAR_CONNECTOR_SHELL_WIDTH_MM / 2,
    360.0 + REAR_CONNECTOR_PROTRUSION_MM,
)


@lru_cache(maxsize=1)
def generate_visual_stl() -> bytes:
    """Return a binary STL of the 360x360 physical surround only.

    The central aperture corresponds exactly to X=0..300, Y=0..305 after the
    slicer's standard model-centering translation. The outer band has regular
    small perforations and 16 machined hex-socket screw seats. The centre has
    a 3 mm thick backing under the separate printable texture; full-depth
    perforations are explicitly modelled on the exposed exterior margin.
    A small rear electrical connector is an approximate photographic mesh.
    This is purely a display asset and NEVER changes movement, bed-mesh or
    placement limits.
    """
    stream = BytesIO()
    name = b'Zortrax M300 Classic 360x360 mm - PRINTABLE 300x305 - VISUAL ONLY'
    stream.write(name.ljust(80,b' '))
    stream.write(pack('<I',0))
    count=0

    def vert(x,y,z):
        # Orca translates a custom bed model by the print area's midpoint
        # (150, 152.5). Therefore physical [0..360] -> printer [-30..330].
        return (x-180.,y-182.5,z)

    def triangle(a,b,c):
        nonlocal count
        ux,uy,uz=(b[i]-a[i] for i in range(3))
        vx,vy,vz=(c[i]-a[i] for i in range(3))
        nx,ny,nz=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx)
        length=sqrt(nx*nx+ny*ny+nz*nz)
        if length: nx,ny,nz=nx/length,ny/length,nz/length
        stream.write(pack('<12fH',nx,ny,nz,*a,*b,*c,0))
        count += 1

    def quad(a,b,c,d):
        triangle(a,b,c)
        triangle(a,c,d)

    def box(x0,y0,x1,y1,z0,z1):
        """Visual cuboid; STL remains independent of the printable geometry."""
        p000,p100,p110,p010=(vert(x0,y0,z0),vert(x1,y0,z0),
                              vert(x1,y1,z0),vert(x0,y1,z0))
        p001,p101,p111,p011=(vert(x0,y0,z1),vert(x1,y0,z1),
                              vert(x1,y1,z1),vert(x0,y1,z1))
        quad(p000,p010,p110,p100) # bottom
        quad(p001,p101,p111,p011) # top
        quad(p000,p100,p101,p001) # front
        quad(p010,p011,p111,p110) # rear
        quad(p000,p001,p011,p010) # left
        quad(p100,p110,p111,p101) # right

    square=(( -1.5,-1.5),(0.,-1.5),(1.5,-1.5),(1.5,0.),
            (1.5,1.5),(0.,1.5),(-1.5,1.5),(-1.5,0.))

    def tile(x0,y0,x1,y1):
        cx,cy=(x0+x1)/2,(y0+y1)/2
        full=abs(x1-x0-3.0)<1e-8 and abs(y1-y0-3.0)<1e-8
        in_field=(14.8 <= cx <= 345.2 and 15.8 <= cy <= 343.2)
        clear=all(hypot(cx-bx,cy-by)>5.0 for bx,by in FRAME_SCREWS)
        if not (full and in_field and clear):
            quad(vert(x0,y0,TOP_Z),vert(x1,y0,TOP_Z),
                 vert(x1,y1,TOP_Z),vert(x0,y1,TOP_Z))
            quad(vert(x0,y0,BOTTOM_Z),vert(x0,y1,BOTTOM_Z),
                 vert(x1,y1,BOTTOM_Z),vert(x1,y0,BOTTOM_Z))
            return

        outer=[(cx+dx,cy+dy) for dx,dy in square]
        inner=[(cx+dx*PERFORATION_RADIUS_MM/hypot(dx,dy),
                cy+dy*PERFORATION_RADIUS_MM/hypot(dx,dy))
               for dx,dy in square]
        for i in range(8):
            j=(i+1)%8
            # Eight exact round-hole sectors with a continuous top and bottom
            # sheet. The vertical inner wall makes each aperture read as a hole.
            quad(vert(*outer[i],TOP_Z),vert(*outer[j],TOP_Z),
                 vert(*inner[j],TOP_Z),vert(*inner[i],TOP_Z))
            quad(vert(*outer[i],BOTTOM_Z),vert(*inner[i],BOTTOM_Z),
                 vert(*inner[j],BOTTOM_Z),vert(*outer[j],BOTTOM_Z))
            quad(vert(*inner[i],BOTTOM_Z),vert(*inner[j],BOTTOM_Z),
                 vert(*inner[j],TOP_Z),vert(*inner[i],TOP_Z))

    # Front 30 mm, rear 25 mm, left and right 30 mm surround.
    for iy in range(120):
        y0,y1=iy*3.,(iy+1)*3.
        for ix in range(120):
            x0,x1=ix*3.,(ix+1)*3.
            if x1<=30 or x0>=330 or y1<=30 or y0>=336:
                tile(x0,y0,x1,y1)
    # Precisely close the 1 mm 335..336 interval along the rear edge.
    for ix in range(10,110):
        tile(ix*3.,335.,(ix+1)*3.,336.)

    # The physical sheet is 3 mm thick ACROSS ITS WHOLE FOOTPRINT.
    # This central backing is slightly below Orca's SVG logo layer, which
    # supplies colours and visible perforations inside the 300x305 polygon.
    # Modelling all central holes in STL as well would create hundreds of
    # thousands of redundant 3D triangles and slow down the GUI.
    box(30.,30.,330.,335.,BOTTOM_Z,TOP_Z)

    def wall(x0,y0,x1,y1):
        quad(vert(x0,y0,BOTTOM_Z),vert(x1,y1,BOTTOM_Z),
             vert(x1,y1,TOP_Z),vert(x0,y0,TOP_Z))
    for edge in ((0,0,360,0),(360,0,360,360),
                 (360,360,0,360),(0,360,0,0),
                 (30,30,30,335),(30,335,330,335),
                 (330,335,330,30),(330,30,30,30)):
        wall(*edge)

    # Real-looking, countersunk metal ALLEN head. The inner socket is
    # hexagonal (not the circular hole used by the previous STL).
    # 24 outer segments; 4 evenly spaced interpolation points per hex side.
    # This only adds decorative geometry; no printer coordinates change.
    def socket_xy(cx, cy, i):
        side,step=divmod(i,4)
        a=(side+0.5)*pi/3
        b=(side+1.5)*pi/3
        t=step/4.
        return (cx + 1.55*((1-t)*cos(a)+t*cos(b)),
                cy + 1.55*((1-t)*sin(a)+t*sin(b)))

    for bx,by in FRAME_SCREWS:
        for i in range(24):
            j=(i+1)%24
            a=2*pi*i/24; b=2*pi*j/24
            def outer(rad, theta, height):
                return vert(bx+rad*cos(theta),by+rad*sin(theta),height)
            def inner(k,height):
                return vert(*socket_xy(bx,by,k),height)
            # Shallow bevel around machined 6.4 mm outer diameter.
            quad(outer(3.35,a,TOP_Z),outer(3.35,b,TOP_Z),
                 outer(3.05,b,TOP_Z+.22),outer(3.05,a,TOP_Z+.22))
            # Flat annulus between screw exterior and the actual hex socket.
            quad(outer(3.05,a,TOP_Z+.22),outer(3.05,b,TOP_Z+.22),
                 inner(j,TOP_Z+.22),inner(i,TOP_Z+.22))
            # Recessed, six-sided socket walls.
            quad(inner(i,TOP_Z+.02),inner(j,TOP_Z+.02),
                 inner(j,TOP_Z+.22),inner(i,TOP_Z+.22))
            triangle(inner(i,TOP_Z+.02),vert(bx,by,TOP_Z+.02),
                     inner(j,TOP_Z+.02))

    # Rear connector photographed with a millimetre ruler. Its cream plastic
    # body is approx. 8-9 mm wide and has two soldered metal attachment wings
    # spanning approximately 12 mm. Its exact Z dimension was not measured.
    left,front,right,rear=REAR_CONNECTOR_SHELL_BOUNDS_MM
    body_bottom=TOP_Z+.38
    body_top=TOP_Z+REAR_CONNECTOR_BODY_HEIGHT_MM
    box(left,front,right,rear,body_bottom,body_top)

    # Narrow base at the rear margin and two visible metal fixing wings.
    x=REAR_CONNECTOR_CENTER_X_MM
    box(x-6.0,356.0,x+6.0,360.2,TOP_Z+.06,TOP_Z+.42)
    box(x-6.0,355.8,left,359.5,TOP_Z+.09,TOP_Z+.58)
    box(right,355.8,x+6.0,359.5,TOP_Z+.09,TOP_Z+.58)

    # Raised central socket cap/back wall and five slender contact ribs.
    box(left+.35,359.1,right-.35,361.4,body_top,body_top+.45)
    for k in range(5):
        sx=x-3.0+k*1.5
        box(sx-.17,359.35,sx+.17,361.45,body_top+.43,body_top+.78)
    # Small visible latch near the interior-facing edge.
    box(x-2.2,354.2,x+2.2,355.1,TOP_Z+.50,TOP_Z+1.30)

    result=stream.getvalue()
    result=bytearray(result)
    result[80:84]=pack('<I',count)
    assert len(result)==84+count*50
    assert count>40000
    return bytes(result)


if __name__=='__main__':
    from pathlib import Path
    target=Path(__file__).resolve().parents[1]/'profiles/Zortrax/model/Zortrax_M300_Classic_visual_bed_360mm.stl'
    target.parent.mkdir(parents=True,exist_ok=True)
    data=generate_visual_stl()
    target.write_bytes(data)
    print(f'Generated {target} ({len(data):,} bytes; {int.from_bytes(data[80:84], "little"):,} facets)')

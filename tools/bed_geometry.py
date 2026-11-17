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
# Two centre screws are on the SVG crop; these 16 frame fasteners lie outside
# the safe printable rectangle. Locations are visual estimates from the photo.
FRAME_SCREWS = tuple((x, y) for x in (17.,97.,180.,263.,343.) for y in (16.,344.)) + tuple((x,y) for y in (98.,180.,262.) for x in (17.,343.))
TOP_Z = .35
BOTTOM_Z = -.35
PERFORATION_PITCH_MM = 3.0
PERFORATION_RADIUS_MM = .76


@lru_cache(maxsize=1)
def generate_visual_stl() -> bytes:
    """Return a binary STL of the 360x360 physical surround only.

    The central aperture corresponds exactly to X=0..300, Y=0..305 after the
    slicer's standard model-centering translation. The outer band has regular
    small perforations and 16 machined hex-socket screw seats. This is purely
    a display asset and NEVER changes movement, bed-mesh or placement limits.
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

    def wall(x0,y0,x1,y1):
        quad(vert(x0,y0,BOTTOM_Z),vert(x1,y1,BOTTOM_Z),
             vert(x1,y1,TOP_Z),vert(x0,y0,TOP_Z))
    for edge in ((0,0,360,0),(360,0,360,360),
                 (360,360,0,360),(0,360,0,0),
                 (30,30,30,335),(30,335,330,335),
                 (330,335,330,30),(330,30,30,30)):
        wall(*edge)

    # Hex-socket bolt heads, entirely on the non-printable rim.
    for bx,by in FRAME_SCREWS:
        for n in range(12):
            a=2*pi*n/12; b=2*pi*(n+1)/12
            def ring(r,theta,z):
                return vert(bx+r*cos(theta),by+r*sin(theta),z)
            quad(ring(3.1,a,.44),ring(3.1,b,.44),
                 ring(1.45,b,.44),ring(1.45,a,.44))
            quad(ring(3.1,a,TOP_Z),ring(3.1,b,TOP_Z),
                 ring(3.1,b,.44),ring(3.1,a,.44))
            quad(ring(1.45,a,.36),ring(1.45,b,.36),
                 ring(1.45,b,.44),ring(1.45,a,.44))
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

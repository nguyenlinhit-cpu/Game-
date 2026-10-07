# Builds the Creed: Ruin icon — a shattered, exploding star with broken rings
# and debris flying outward. Run: blender -b creed_ruin_icon.blend --python build_ruin_icon.py
import bpy, bmesh, math, random

R = random.Random(13)
OUT_DIR = bpy.path.abspath('//')

vl = bpy.context.view_layer.layer_collection
for name in ('CreedFury', 'CreedFury_v1'):
    if name in vl.children:
        vl.children[name].exclude = True

col = bpy.data.collections.get('CreedRuin')
if col:
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new('CreedRuin')
    bpy.context.scene.collection.children.link(col)

W = bpy.data.materials['HSR_White']
G = bpy.data.materials['HSR_Grey']


def rot(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0]*c - p[1]*s, p[0]*s + p[1]*c)


def centroid(poly):
    return (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))


def xform(poly, center, move, ang):
    out = []
    for x, y in poly:
        dx, dy = rot((x-center[0], y-center[1]), ang)
        out.append((center[0]+dx+move[0], center[1]+dy+move[1]))
    return out


def burst(poly, dist, spin):
    """Push a piece radially away from the origin and spin it about its centroid."""
    c = centroid(poly)
    L = math.hypot(*c) or 1
    return xform(poly, c, (c[0]/L*dist, c[1]/L*dist), spin)


def lerp(p, q, t):
    return (p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t)


def build(name, polys, mat, z):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for poly in polys:
        bm.faces.new([bm.verts.new((x, y, 0)) for x, y in poly])
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location.z = z
    me.materials.append(mat)
    col.objects.link(ob)
    return ob


# ---------- shattered 8-point star ----------
star_w, star_g = [], []
N, inner = 8, 1.05
for i in range(N):
    a = math.pi/2 + i*2*math.pi/N
    long_ = i % 2 == 0
    tip_r = 3.1 if long_ else 2.1
    tip = (math.cos(a)*tip_r, math.sin(a)*tip_r)
    vl_ = (math.cos(a-math.pi/N)*inner, math.sin(a-math.pi/N)*inner)
    vr_ = (math.cos(a+math.pi/N)*inner, math.sin(a+math.pi/N)*inner)
    base = (math.cos(a)*0.45, math.sin(a)*0.45)
    k = 0.55 if long_ else 0.6
    mid = lerp(base, tip, k)
    sgn = 1 if i % 3 else -1
    midj = (mid[0] + math.cos(a+math.pi/2)*0.07*sgn, mid[1] + math.sin(a+math.pi/2)*0.07*sgn)
    el, er = lerp(vl_, tip, k*0.8), lerp(vr_, tip, k*0.8)
    s = 1 if R.random() > 0.5 else -1
    d0 = 0.25 + R.uniform(0, 0.15)
    star_w.append(burst([base, vl_, el, midj], d0, s*R.uniform(0.02, 0.08)))
    star_g.append(burst([base, midj, er, vr_], d0+0.08, -s*R.uniform(0.02, 0.08)))
    d1 = d0 + (0.55 if long_ else 0.45) + R.uniform(0, 0.2)
    star_w.append(burst([midj, el, tip], d1, s*R.uniform(0.08, 0.2)))
    star_g.append(burst([midj, tip, er], d1+0.12, -s*R.uniform(0.08, 0.2)))

build('Ruin_Star_Light', star_w, W, 0.30)
build('Ruin_Star_Shade', star_g, G, 0.30)

# glowing core: a small four-point spark left where the star broke
build('Ruin_Core', [[(0, 0.62), (-0.2, 0), (0, -0.62), (0.2, 0)],
                    [(-0.62, 0), (0, 0.2), (0.62, 0), (0, -0.2)]], W, 0.40)


# ---------- broken rings ----------
def arc(r0, r1, a0, a1, jag=0.06):
    n = max(3, int(abs(a1-a0)/0.06))
    outer = [(math.cos(a0+(a1-a0)*t/n)*r1, math.sin(a0+(a1-a0)*t/n)*r1) for t in range(n+1)]
    inner_ = [(math.cos(a1-(a1-a0)*t/n)*r0, math.sin(a1-(a1-a0)*t/n)*r0) for t in range(n+1)]
    rm = (r0+r1)/2
    e1 = (math.cos(a1+jag)*rm, math.sin(a1+jag)*rm)  # jagged break tips
    e0 = (math.cos(a0-jag*0.6)*rm, math.sin(a0-jag*0.6)*rm)
    return outer + [e1] + inner_ + [e0]


def broken_ring(r0, r1, nseg, gap, push, spin, phase):
    cuts = sorted(phase + i*2*math.pi/nseg + R.uniform(-0.18, 0.18) for i in range(nseg))
    polys = []
    for i in range(nseg):
        a0 = cuts[i] + gap/2
        a1 = cuts[(i+1) % nseg] + (2*math.pi if i == nseg-1 else 0) - gap/2
        polys.append(burst(arc(r0, r1, a0, a1), R.uniform(*push), R.choice((-1, 1))*R.uniform(*spin)))
    return polys


build('Ruin_Ring_Inner', broken_ring(3.05, 3.35, 7, 0.22, (0.0, 0.25), (0.0, 0.06), 0.3), G, 0.10)
build('Ruin_Ring_Outer', broken_ring(3.85, 4.0, 11, 0.16, (0.05, 0.45), (0.02, 0.1), 0.0), W, 0.12)

# ---------- debris shards, evenly spread by angle so the chaos stays balanced ----------
deb_w, deb_g = [], []
M = 30
for i in range(M):
    a = i*2*math.pi/M + R.uniform(-0.08, 0.08)
    r = R.uniform(2.1, 4.9)
    sz = 0.24 * (1.25 - (r-2.1)/4.0) * R.uniform(0.6, 1.2)
    c = (math.cos(a)*r, math.sin(a)*r)
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    ln = sz*R.uniform(1.6, 2.6)
    tri = [(c[0]+d[0]*ln, c[1]+d[1]*ln),
           (c[0]+n[0]*sz*0.5 - d[0]*sz*0.3, c[1]+n[1]*sz*0.5 - d[1]*sz*0.3),
           (c[0]-n[0]*sz*0.6 - d[0]*sz*0.4, c[1]-n[1]*sz*0.6 - d[1]*sz*0.4)]
    (deb_w if i % 2 else deb_g).append(xform(tri, c, (0, 0), R.uniform(-0.5, 0.5)))
build('Ruin_Debris_Light', deb_w, W, 0.20)
build('Ruin_Debris_Shade', deb_g, G, 0.20)

# ---------- explosion rays between the star points ----------
rays = []
for i in range(16):
    a = math.pi/2 + math.pi/8 + i*2*math.pi/16 + R.uniform(-0.05, 0.05)
    r0 = R.uniform(1.3, 1.6)
    r1 = r0 + R.uniform(0.9, 1.4) * (1.0 if i % 2 else 0.7)
    w = 0.05 if i % 2 else 0.035
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    rm = r0 + (r1-r0)*0.35
    rays.append([(d[0]*r0, d[1]*r0), (d[0]*rm+n[0]*w, d[1]*rm+n[1]*w),
                 (d[0]*r1, d[1]*r1), (d[0]*rm-n[0]*w, d[1]*rm-n[1]*w)])
build('Ruin_Rays', rays, G, 0.05)

bpy.ops.wm.save_mainfile()

# renders: transparent icon, plus a preview on the navy background
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = OUT_DIR + 'creed_ruin_icon.png'
bpy.ops.render.render(write_still=True)
bg = bpy.data.objects['Preview_BG']
bg.hide_render = False
scene.render.filepath = OUT_DIR + 'creed_ruin_preview.png'
bpy.ops.render.render(write_still=True)
bg.hide_render = True
print('DONE', [o.name for o in col.objects])

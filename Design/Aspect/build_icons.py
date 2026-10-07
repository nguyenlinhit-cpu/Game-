"""Sinh bộ biểu tượng nguyên tố phong cách glyph khối (cảm hứng HSR).

Chạy: python3 build_icons.py  -> tạo <Elem>/<elem>_glyph.svg
Rồi:  resvg -w 1024 -h 1024 file.svg file.png
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
C = 256  # tâm khung 512x512


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def poly(pts, fill="#fff", extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}" {extra}/>'


def rot(pts, deg, cx=C, cy=C):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def shift(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def mirror(pts):
    return [(2 * C - x, y) for x, y in reversed(pts)]


def cut_stroke(d_or_pts, w, is_path=False):
    if is_path:
        return f'<path d="{d_or_pts}" fill="none" stroke="#000" stroke-width="{w}" stroke-linejoin="round"/>'
    return f'<polygon points="{P(d_or_pts)}" fill="none" stroke="#000" stroke-width="{w}" stroke-linejoin="miter"/>'


def svg(name, top, bot, glow, mask, shade="", extra=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>
  </linearGradient>
  <mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512">{mask}</mask>
  <filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<g filter="url(#blur)" opacity="0.55"><rect width="512" height="512" fill="{glow}" mask="url(#m)"/></g>
<rect width="512" height="512" fill="url(#g)" mask="url(#m)"/>
<g mask="url(#m)">{shade}</g>
{extra}
</svg>'''


W = "#fff"
K = "#000"
icons = {}

# ---------------- EMBER: ngọn lửa 3 lưỡi, lõi than hồng hình thoi ----------------
flame_l = "M256,472 C178,472 106,416 106,336 C106,270 146,230 138,170 C186,204 202,250 200,290 C206,214 226,128 256,34"
flame = flame_l + " C286,128 306,214 312,290 C310,250 326,204 374,170 C366,230 406,270 406,336 C406,416 334,472 256,472 Z"
inner = "M256,430 C210,430 176,398 176,352 C176,316 196,296 204,262 C226,292 236,314 236,330 C242,292 248,262 256,226 C264,262 270,292 276,330 C276,314 286,292 308,262 C316,296 336,316 336,352 C336,398 302,430 256,430 Z"
core = [(256, 318), (290, 372), (256, 418), (222, 372)]
icons["Ember"] = svg(
    "ember", "#ffd46a", "#e2381c", "#ff6a2a",
    mask=f'<path d="{flame}" fill="{W}"/>'
         f'<path d="{inner}" fill="none" stroke="{K}" stroke-width="11"/>'
         + poly(shift(rot([(256, 62), (266, 80), (256, 98), (246, 80)], 0), -112, 30), W)
         + poly(shift([(256, 62), (266, 80), (256, 98), (246, 80)], 116, 4), W)
         + poly([(256, 300), (304, 372), (256, 436), (208, 372)], K),
    shade="",
    extra=poly(core, "#fff3c0") + poly([(256, 318), (290, 372), (256, 372)], "#ffffff")
          + poly([(256, 372), (290, 372), (256, 418)], "#ff9a3c") + poly([(222, 372), (256, 372), (256, 418)], "#ffc75a"),
)

# ---------------- FROST: cụm tinh thể băng lục giác mọc từ gốc ----------------
def shard(cx, top, bot, hw, tip):
    return [(cx, top), (cx + hw, top + tip), (cx + hw, bot - tip * 0.6), (cx, bot), (cx - hw, bot - tip * 0.6), (cx - hw, top + tip)]

center = shard(256, 30, 452, 46, 74)
side = shard(256, 120, 430, 32, 52)
small = shard(256, 210, 420, 22, 36)
sides = [rot(side, a, 256, 440) for a in (-34, 34)] + [rot(small, a, 256, 440) for a in (-66, 66)]
frost_mask = "".join(poly(s, W) for s in sides[2:])
frost_mask += "".join(cut_stroke(s, 14) for s in sides[:2]) + "".join(poly(s, W) for s in sides[:2])
frost_mask += cut_stroke(center, 16) + poly(center, W)
# rãnh băng nứt trong thân trụ chính
frost_mask += f'<path d="M256,150 L240,200 L262,250 L246,300" fill="none" stroke="{K}" stroke-width="7" stroke-linejoin="miter"/>'
# hạt tuyết
for x, y, s in ((120, 120, 16), (392, 110, 12), (408, 210, 9)):
    frost_mask += poly([(x, y - s), (x + s * .6, y), (x, y + s), (x - s * .6, y)], W)
frost_shade = "".join(poly([(256 if i == 0 else 0, 0)] + [], "none") for i in range(0))
# mặt phải mỗi tinh thể tối hơn -> cảm giác lăng trụ
for s in [center] + sides:
    cx = sum(p[0] for p in (s[0], s[3])) / 2
    frost_shade += poly([s[0], s[1], s[2], s[3]], "#0a2a6a", 'opacity="0.28"')
icons["Frost"] = svg("frost", "#effaff", "#3f8ff0", "#6cc8ff", frost_mask, frost_shade)

# ---------------- STORM: tia sét bổ đôi vòng mây xoáy ----------------
bolt = [(286, 26), (376, 26), (300, 196), (378, 196), (184, 490), (236, 278), (156, 278)]
ring = ""
R = 196
for a0, a1 in ((-60, 20), (120, 200)):  # 2 cung xoáy đối xứng
    pts_o, pts_i = [], []
    for i in range(41):
        t = i / 40
        a = math.radians(a0 + (a1 - a0) * t)
        w = 26 * math.sin(math.pi * t) ** 0.7
        pts_o.append((C + (R + w / 2) * math.cos(a), C + (R + w / 2) * math.sin(a)))
        pts_i.append((C + (R - w / 2) * math.cos(a), C + (R - w / 2) * math.sin(a)))
    ring += poly(pts_o + pts_i[::-1], W)
fork_l = [(196, 300), (120, 330), (148, 350), (78, 404), (168, 340), (142, 324), (210, 300)]
fork_r = [(330, 210), (402, 186), (382, 172), (448, 120), (370, 162), (392, 176), (322, 196)]
storm_mask = ring + poly(fork_l, W) + poly(fork_r, W) + cut_stroke(bolt, 22) + poly(bolt, W)
storm_mask += f'<path d="M318,52 L262,190" stroke="{K}" stroke-width="7"/>'
for x, y, s in ((112, 150, 14), (410, 360, 14), (380, 420, 9)):
    storm_mask += poly([(x, y - s), (x + s * .6, y), (x, y + s), (x - s * .6, y)], W)
storm_shade = poly([(331, 26), (376, 26), (300, 196), (378, 196), (184, 490), (270, 236)], "#2a0050", 'opacity="0.22"')
icons["Storm"] = svg("storm", "#f6d8ff", "#8b2fe0", "#b45cff", storm_mask, storm_shade)

# ---------------- GALE: ba lưỡi gió xoáy quanh mắt bão ----------------
def blade(a0, span, r0, r1, wmax):
    out, inn = [], []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + span * t)
        r = r0 + (r1 - r0) * t
        w = wmax * (math.sin(math.pi * min(1, t * 1.15)) ** 0.75)
        out.append((C + (r + w * .5) * math.cos(a), C + (r + w * .5) * math.sin(a)))
        inn.append((C + (r - w * .5) * math.cos(a), C + (r - w * .5) * math.sin(a)))
    return out + inn[::-1]

gale_mask = ""
for k in range(3):
    base = -90 + k * 120
    gale_mask += poly(blade(base, 150, 70, 214, 58), W)
    gale_mask += poly(blade(base + 40, 105, 150, 236, 14), W)  # vệt gió mảnh bên ngoài
gale_mask += f'<circle cx="256" cy="256" r="44" fill="{W}"/><circle cx="256" cy="256" r="26" fill="{K}"/>'
gale_mask += f'<circle cx="256" cy="256" r="10" fill="{W}"/>'
icons["Gale"] = svg("gale", "#d8ffe9", "#14a77a", "#3fe0a8", gale_mask)

# ---------------- RIFT: viên thoi bị xé đôi, ánh sáng hư không lọt qua khe ----------------
zig = [(256, 40), (232, 132), (278, 200), (236, 284), (280, 364), (256, 472)]
left = [(72, 256)] + zig
right = zig[::-1] + [(440, 256)]
L = shift(left, -26, 14)
Rr = shift(right, 26, -14)
def inset(pts, f):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in pts]
rift_mask = poly(L, W) + poly(Rr, W)
rift_mask += cut_stroke(inset(L, .62), 9) + cut_stroke(inset(Rr, .62), 9)
star = [(256, 4), (270, 242), (330, 256), (270, 270), (256, 508), (242, 270), (182, 256), (242, 242)]
rift_shade = poly(Rr, "#10003a", 'opacity="0.25"')
icons["Rift"] = svg("rift", "#c9d2ff", "#3a2ab8", "#6a5cff", rift_mask, rift_shade,
                    extra=f'<g filter="url(#blur)" opacity=".8">{poly(star, "#b8a8ff")}</g>' + poly(star, "#ffffff"))

# ---------------- CHRONO: đồng hồ cát đóng băng trong vòng mặt số ----------------
chrono_mask = f'<circle cx="256" cy="256" r="206" fill="none" stroke="{W}" stroke-width="20"/>'
for i in range(12):
    a = math.radians(i * 30)
    l = 34 if i % 3 == 0 else 18
    x0, y0 = C + 206 * math.cos(a), C + 206 * math.sin(a)
    x1, y1 = C + (206 - 10 - l) * math.cos(a), C + (206 - 10 - l) * math.sin(a)
    chrono_mask += f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{W}" stroke-width="{12 if i % 3 == 0 else 7}"/>'
glass = ("M150,92 L362,92 C362,170 300,214 274,256 C300,298 362,342 362,420 L150,420 "
         "C150,342 212,298 238,256 C212,214 150,170 150,92 Z")
chrono_mask += f'<path d="{glass}" fill="none" stroke="{K}" stroke-width="44" stroke-linejoin="round"/>'
chrono_mask += f'<path d="{glass}" fill="none" stroke="{W}" stroke-width="20" stroke-linejoin="round"/>'
chrono_mask += f'<rect x="124" y="56" width="264" height="34" rx="8" fill="{W}"/><rect x="124" y="422" width="264" height="34" rx="8" fill="{W}"/>'
# cát trên (đứng yên), dòng cát bị ngắt quãng (thời gian ngừng), cát dưới
chrono_mask += f'<path d="M190,170 L322,170 C306,206 278,226 262,246 L250,246 C234,226 206,206 190,170 Z" fill="{W}"/>'
chrono_mask += "".join(f'<rect x="251" y="{y}" width="10" height="14" fill="{W}"/>' for y in (270, 300, 330))
chrono_mask += f'<path d="M184,396 C200,360 236,350 256,350 C276,350 312,360 328,396 Z" fill="{W}"/>'
chrono_shade = ""
icons["Chrono"] = svg("chrono", "#fffbe6", "#d79a2c", "#ffd98a", chrono_mask, chrono_shade)

# ---------------- MIGHT: nắm đấm thép giáng xuống, sóng chấn động ----------------
might_mask = ""
fx = [150, 204, 258, 312]
for x in fx:
    might_mask += f'<rect x="{x}" y="104" width="52" height="132" rx="20" fill="{W}"/>'
might_mask += f'<rect x="150" y="170" width="214" height="196" rx="26" fill="{W}"/>'
for x in fx[1:]:
    might_mask += f'<line x1="{x - 1}" y1="112" x2="{x - 1}" y2="214" stroke="{K}" stroke-width="7"/>'
might_mask += f'<rect x="150" y="214" width="214" height="7" fill="{K}"/>'  # rãnh đốt ngón
thumb = "M128,250 C128,232 142,226 158,226 L292,226 C312,226 320,242 320,256 C320,272 308,286 290,286 L176,286 C150,286 128,276 128,250 Z"
might_mask += f'<path d="{thumb}" fill="none" stroke="{K}" stroke-width="16"/><path d="{thumb}" fill="{W}"/>'
might_mask += f'<path d="M176,366 L338,366 L326,420 L188,420 Z" fill="{W}"/>'
might_mask += f'<rect x="176" y="366" width="162" height="10" fill="{K}"/>'
might_mask += f'<path d="M162,432 L352,432 L340,468 L174,468 Z" fill="{W}"/>'
# tia chấn động hai bên
for sgn in (-1, 1):
    for th, ln, w in ((-28, 58, 16), (0, 74, 20), (28, 58, 16)):
        a = math.radians(th)
        bx, by = 256 + sgn * 132, 262 + th * 3.4
        dx, dy = sgn * math.cos(a), math.sin(a)
        tip = (bx + dx * (ln + 30), by + dy * (ln + 30))
        b0 = (bx + dx * 30, by + dy * 30)
        might_mask += poly([(b0[0] - dy * w / 2, b0[1] + dx * w / 2), tip, (b0[0] + dy * w / 2, b0[1] - dx * w / 2)], W)
might_shade = '<rect x="0" y="300" width="512" height="212" fill="#3a0008" opacity="0.15"/>'
icons["Might"] = svg("might", "#ffd0c8", "#c0182c", "#ff3a4a", might_mask, might_shade)

for elem, s in icons.items():
    path = os.path.join(HERE, elem, f"{elem.lower()}_glyph.svg")
    with open(path, "w") as f:
        f.write(s)
    print(path)

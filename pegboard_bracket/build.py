"""Generate pegboard_bracket.stl + preview.png (mirrors pegboard_bracket.scad; no OpenSCAD needed)."""
import sys
import numpy as np
import manifold3d as m3d
import trimesh

P = dict(rail_w=45.1, fit_gap=0.3, tape_t=1.0, lip_h=10, board_t=5.0, board_gap=0.4,
         board_off=0, len=40, wall=4, floor_t=5, slot_h=30, cheek_t=5, chamfer=1.2, bolt_d=4.4)
for a in sys.argv[1:]:
    k, v = a.split("=")
    P[k] = float(v)

ri = P["rail_w"] / 2 + P["fit_gap"]; ro = ri + P["wall"]
zf = P["tape_t"]; zt = zf + P["floor_t"]; zh = zt + P["slot_h"]
s = (P["board_t"] + P["board_gap"]) / 2; o = P["board_off"]; c = P["chamfer"]
c0 = o - s - P["cheek_t"]; c1 = o + s + P["cheek_t"]; L = P["lip_h"]

outer = [(-ro, -L), (-ri, -L), (-ri, zf), (ri, zf), (ri, -L), (ro, -L), (ro, zt), (c1, zh), (c0, zh), (-ro, zt)]
slot = [(o - s, zt), (o + s, zt), (o + s, zh - c), (o + s + c, zh + 0.01), (o - s - c, zh + 0.01), (o - s, zh - c)]

def ext(poly):  # CCW polygon in (Y,Z) -> solid extruded along +X
    pts = np.array(poly)
    area = 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
    if area < 0: pts = pts[::-1]
    sol = m3d.Manifold.extrude(m3d.CrossSection([pts.tolist()]), P["len"])
    return sol  # profile in XY, extruded along Z; axes remapped after meshing

body = ext(outer) - ext(slot)
mesh = body.to_mesh()
V = np.array(mesh.vert_properties)[:, :3]
V = V[:, [2, 0, 1]]  # (Y,Z,X) -> (X,Y,Z); cyclic, so winding stays valid
tm = trimesh.Trimesh(V, np.array(mesh.tri_verts))
if P["bolt_d"] > 0:
    cyl = trimesh.creation.cylinder(radius=P["bolt_d"] / 2, height=4 * ro, sections=32)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    cyl.apply_translation([P["len"] / 2, 0, zt + P["slot_h"] * 0.55])
    a = m3d.Manifold(m3d.Mesh(tm.vertices.astype(np.float32), tm.faces.astype(np.uint32)))
    b = m3d.Manifold(m3d.Mesh(cyl.vertices.astype(np.float32), cyl.faces.astype(np.uint32)))
    r = (a - b).to_mesh()
    tm = trimesh.Trimesh(np.array(r.vert_properties)[:, :3], np.array(r.tri_verts))

print("watertight:", tm.is_watertight, "volume cm3: %.1f" % (tm.volume / 1000), "bbox:", tm.bounds.round(2).tolist())
tm.export("pegboard_bracket.stl")

# ---- preview: section + 3D ----
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig = plt.figure(figsize=(13, 6))
ax = fig.add_subplot(1, 2, 1)
ax.fill(*zip(*outer), color="#4a7ab8", alpha=.85, label="bracket")
ax.fill(*zip(*slot), color="white")
ax.add_patch(plt.Rectangle((-P["rail_w"] / 2, -40), P["rail_w"], 40, color="#bbb", label="rail 45.1"))
ax.add_patch(plt.Rectangle((-P["rail_w"] / 2 + 2, 0), P["rail_w"] - 4, zf, color="#e6a23c", label="nano tape"))
ax.add_patch(plt.Rectangle((o - P["board_t"] / 2, zt), P["board_t"], 70, color="#8d6e63", alpha=.6, label="pegboard"))
ax.set_aspect("equal"); ax.set_xlim(-45, 45); ax.set_ylim(-42, 85); ax.grid(alpha=.3)
ax.set_title("Section (mm), Z=0 = rail top = 350 mm above desk"); ax.legend(loc="upper right", fontsize=8)
ax3 = fig.add_subplot(1, 2, 2, projection="3d")
ax3.add_collection3d(Poly3DCollection(tm.vertices[tm.faces], facecolor="#4a7ab8", edgecolor="#22344d", linewidths=.15, alpha=.95))
b = tm.bounds; ax3.set_xlim(b[0][0], b[1][0]); ax3.set_ylim(b[0][1], b[1][1]); ax3.set_zlim(b[0][2], b[1][2])
ax3.set_box_aspect(b[1] - b[0]); ax3.view_init(25, -55); ax3.set_title("3D")
plt.tight_layout(); plt.savefig("preview.png", dpi=110)

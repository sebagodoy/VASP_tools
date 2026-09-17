#!/usr/bin/env python3

import numpy as np
import pyvista as pv
from docutils.nodes import enumerated_list
from scipy.spatial import ConvexHull
import vtk

# Numerical tolerance for ray/triangle intersection
TOL = 1e-8

# ============================================================
# 1. Points in 3D and scalar F values
# ============================================================
iDir = input('  >> ACF bader charge file (def=.) :') or './'
print(f"     Looking for {iDir}ACF.dat")
with open(iDir+'ACF.dat') as f:
    iData = f.readlines()[2:-4]
iCharge = np.array([float(i.split()[4]) for i in iData])
iPos = np.array([[float(i.split()[j]) for j in range(1, 4)] for i in iData])

# Fix charge
print(f"     Got positions and integral density for {len(iCharge)} atoms.")
print("  >> Reference NELEC Cu=11, O=6, C=4, H=1")
iRefInp = input("  >> Reference charges (e.g. 2x20 3x15 ... ) : ")
iRef = []
for i in iRefInp.split():
    for j in range(int(i.split('x')[0])):
        iRef.append(float(i.split('x')[1]))
if not len(iRef) == len(iCharge):
    raise SyntaxError(f" The sequece has {len(iRef)}, but should have {len(iCharge)}")
iChargeCorr = np.array([i - j for i, j in zip(iCharge, iRef)])

points = iPos
F = iChargeCorr
print(f"     > Total electrons : {sum(iCharge)}")
print(f"     > Net charge      : {sum(iChargeCorr)}")
print(f"     > Min : {min(iChargeCorr)} ; Max : {max(iChargeCorr)}")
iLims_sugg = "{:.4f}".format(max([-min(iChargeCorr), max(iChargeCorr)]))
iLims = input(f"  >> Mapping limits (rec=\"{iLims_sugg}\" or \"-{iLims_sugg} {iLims_sugg}\") : ") or iLims_sugg
if len(iLims.split()) == 1:
    F_min = -float(iLims); F_max = float(iLims)
elif len(iLims.split()) == 2:
    F_min = float(iLims.split()[0]); F_max = float(iLims.split()[1])
else:
    raise NotImplementedError(" What?")
print(" Plotting ... ")

# ============================================================
# 2. Calculate the 3D convex hull
# ============================================================
# ============================================================
# CONVEX HULL
# ============================================================

hull = ConvexHull(points)

faces = hull.simplices


# ============================================================
# PYVISTA MESH
# ============================================================

faces_pv = np.hstack([
    np.column_stack([
        np.full(len(faces), 3),
        faces
    ])
]).astype(np.int64).ravel()

mesh = pv.PolyData(points, faces_pv)

mesh.point_data["F"] = F


# ============================================================
# PLOTTER
# ============================================================
plotter = pv.Plotter()

# Hull
plotter.add_mesh( mesh, scalars="F",
    cmap="viridis", clim=[F_min, F_max],
    show_edges=True, edge_color="black", line_width=1.5, opacity=1.0, smooth_shading=False)

# Points
plotter.add_points(points, scalars=F,
    cmap="viridis", clim=[F_min, F_max], point_size=12,
    render_points_as_spheres=True, show_scalar_bar=False)

# ============================================================
# RAY / TRIANGLE INTERSECTION
# ============================================================

def ray_triangle_intersection(origin, direction, v0, v1, v2):
    """
    Möller-Trumbore ray/triangle intersection.

    Returns the distance t along the ray if an intersection
    occurs, otherwise None.
    """
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(direction, edge2)
    a = np.dot(edge1, h)
    if abs(a) < TOL:
        return None
    f = 1.0 / a
    s = origin - v0

    u = f * np.dot(s, h)

    if u < 0.0 or u > 1.0:
        return None

    q = np.cross(s, edge1)
    v = f * np.dot(direction, q)

    if v < 0.0 or u + v > 1.0:
        return None

    t = f * np.dot(edge2, q)

    if t > TOL:
        return t

    return None


# ============================================================
# DETERMINE VISIBLE VERTICES
# ============================================================

def get_visible_points():
    # Camera position
    camera_position = np.array( plotter.camera.position, dtype=float )
    visible = np.ones(len(points), dtype=bool)

    for i, point in enumerate(points):
        # Vector from camera to point
        ray = point - camera_position
        distance_to_point = np.linalg.norm(ray)
        if distance_to_point < TOL:
            continue
        direction = ray / distance_to_point
        # Test whether another hull face blocks the point
        for face in faces:
            # Skip faces containing the point itself.
            if i in face:
                continue
            v0, v1, v2 = points[face]
            t = ray_triangle_intersection( camera_position, direction, v0, v1, v2 )

            if t is not None:
                # Intersection before the target point
                if t < distance_to_point - TOL:
                    visible[i] = False
                    break
    return visible

# ============================================================
# LABEL ACTOR
# ============================================================
labels = [f"{i+1}:"+f"{value:+.2f}" for i, value in enumerate(F)]
label_actor = None

def update_labels(*args):
    global label_actor
    visible = get_visible_points()
    visible_indices = np.where(visible)[0]
    visible_points = points[visible_indices]
    visible_labels = [labels[i] for i in visible_indices ]
    # Remove previous labels
    if label_actor is not None:
        plotter.remove_actor(label_actor)
    # Add labels for visible points
    if len(visible_points) > 0:
        label_actor = plotter.add_point_labels(visible_points, visible_labels,
            point_size=12, font_size=14, text_color="black",
            shape=None, always_visible=True, show_points=False)

# ============================================================
# INITIAL LABELS
# ============================================================
plotter.render()
update_labels()

# ============================================================
# UPDATE LABELS AFTER CAMERA MOVEMENT
# ============================================================
plotter.iren.add_observer("EndInteractionEvent", update_labels)

# ============================================================
# OTHER PLOT ELEMENTS
# ============================================================
#plotter.add_scalar_bar( title="F", n_labels=6)
plotter.show_axes()
plotter.add_text("3D Convex Hull with F", position="upper_left", font_size=14)

# ============================================================
# SHOW
# ============================================================
plotter.show()

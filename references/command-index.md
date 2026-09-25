# Command index

Every entry from the GDL Reference Guide (Archicad 29), with its syntax line and the
page it is documented on. Look a command up here BEFORE writing it. If it is not in
this file, it is not a GDL command — say so instead of inventing one.

To read the full documentation of a command, run:

    python3 scripts/manual.py <COMMAND>

which prints the manual pages for it. Do that whenever the syntax line alone is not
enough — parameter meanings, status codes and restrictions live in the prose.

Entries with no syntax line are section headings or value tables; open their pages
with `manual.py --pages N-M`.

Format: `NAME` — syntax — p.PAGE



## Coordinate Transformations


### 2D Transformations

- `ADD2` — `ADD2 x, y` — p.50
- `MUL2` — `MUL2 x, y` — p.50
- `ROT2` — `ROT2 alpha` — p.51

### 3D Transformations

- `ADDX` — `ADDX dx` — p.51
- `ADDY` — `ADDY dy` — p.51
- `ADDZ` — `ADDZ dz` — p.51
- `ADD` — `ADD dx, dy, dz` — p.51
- `MULX` — `MULX mx` — p.52
- `MULY` — `MULY my` — p.52
- `MULZ` — `MULZ mz` — p.52
- `MUL` — `MUL mx, my, mz` — p.52
- `ROTX` — `ROTX alphax` — p.52
- `ROTY` — `ROTY alphay` — p.52
- `ROTZ` — `ROTZ alphaz` — p.53
- `ROT` — `ROT x, y, z, alpha` — p.53
- `XFORM` — `XFORM newx_x, newy_x, newz_x, offset_x, newx_y, newy_y, newz_y, offset_y, newx_z, newy_z, newz_z, offset_z` — p.53

### Managing the Transformation Stack

- `DEL` — `DEL n [, begin_with]` — p.54
- `DEL TOP` — `DEL TOP` — p.54
- `NTR` — `NTR ()` — p.54

## 3D Shapes


### Basic Shapes

- `BLOCK` — `BLOCK a, b, c` — p.56
- `BRICK` — `BRICK a, b, c` — p.56
- `CYLIND` — `CYLIND h, r` — p.57
- `SPHERE` — `SPHERE r` — p.57
- `ELLIPS` — `ELLIPS h, r` — p.58
- `CONE` — `CONE h, r1, r2, alpha1, alpha2` — p.59
- `PRISM` — `PRISM n, h, x1, y1, ..., xn, yn` — p.59
- `PRISM_` — `PRISM_ n, h, x1, y1, s1, ..., xn, yn, sn` — p.60
- `CPRISM_` — `CPRISM_ top_material, bottom_material, side_material, n, h, x1, y1, s1, ..., xn, yn, sn` — p.63
- `CPRISM_{2}` — `CPRISM_{2} top_material, bottom_material, side_material, n, h, x1, y1, alpha1, s1, mat1, ...` — p.64
- `CPRISM_{3}` — `CPRISM_{3} top_material, bottom_material, side_material, mask, n, h, x1, y1, alpha1, s1, mat1, ...` — p.65
- `CPRISM_{4}` — `CPRISM_{4} top_material, bottom_material, side_material, mask, n, h, x1, y1, alpha1, s1, mat1, ...` — p.68
- `BPRISM_` — `BPRISM_ top_material, bottom_material, side_material, n, h, radius, x1, y1, s1, ...` — p.68
- `FPRISM_` — `FPRISM_ top_material, bottom_material, side_material, hill_material, n, thickness, angle, hill_height, x1, y1, s1, ...` — p.69
- `HPRISM_` — `HPRISM_ top_mat, bottom_mat, side_mat, hill_mat, n, thickness, angle, hill_height, status, x1, y1, s1, ...` — p.71
- `SPRISM_` — `SPRISM_ top_material, bottom_material, side_material, n, xb, yb, xe, ye, h, angle, x1, y1, s1, ...` — p.72
- `SPRISM_{2}` — `SPRISM_{2} top_material, bottom_material, side_material, n, xtb, ytb, xte, yte, topz, tangle, xbb, ybb, xbe, ybe, bottomz, bangle, x1, y1, s1, mat1, ...` — p.73
- `SPRISM_{3}` — `SPRISM_{3} top_material, bottom_material, side_material, mask, n, xtb, ytb, xte, yte, topz, tangle, xbb, ybb, xbe, ybe, bottomz, bangle, x1, y1, s1, mat1, ...` — p.74
- `SPRISM_{4}` — `SPRISM_{4} top_material, bottom_material, side_material, mask, n, xtb, ytb, xte, yte, topz, tangle, xbb, ybb, xbe, ybe, bottomz, bangle, x1, y1, s1, mat1, ...` — p.75
- `SLAB` — `SLAB n, h, x1, y1, z1, ..., xn, yn, zn` — p.76
- `SLAB_` — `SLAB_ n, h, x1, y1, z1, s1, ..., xn, yn, zn, sn` — p.76
- `CSLAB_` — `CSLAB_ top_material, bottom_material, side_material, n, h, x1, y1, z1, s1, ..., xn, yn, zn, sn` — p.77
- `CWALL_` — `CWALL_ left_material, right_material, side_material, height, x1, x2, x3, x4, t, mask1, mask2, mask3, mask4, n, x_start1, y_low1, x_end1, y_high1, frame_shown1, ...` — p.77
- `BWALL_` — `BWALL_ left_material, right_material, side_material, height, x1, x2, x3, x4, t, radius, mask1, mask2, mask3, mask4, n, x_start1, y_low1, x_end1, y_high1, frame_shown1, ...` — p.81
- `XWALL_` — `XWALL_ left_material, right_material, vertical_material, horizontal_material, height, x1, x2, x3, x4, y1, y2, y3, y4, t, radius, log_height, log_offset, mask1, mask2, mask3, mask4, n, x_start1, y_low1, x_end1, y_high1,` — p.83
- `XWALL_{2}` — `XWALL_{2} left_material, right_material, vertical_material, horizontal_material, height, x1, x2, x3, x4, y1, y2, y3, y4, t, radius, log_height, log_offset, mask1, mask2, mask3, mask4, n, x_start1, y_low1, x_end1, y_high1,` — p.85
- `XWALL_{3}` — `XWALL_{3} left_material, right_material, vertical_material, horizontal_material, height, x1, x2, x3, x4, y1, y2, y3, y4, t, radius, log_height, log_offset, mask1, mask2, mask3, mask4, n, x_start1, y_low1, x_end1, y_high1,` — p.86
- `BEAM` — `BEAM left_material, right_material, vertical_material, top_material, bottom_material, height, x1, x2, x3, x4, y1, y2, y3, y4, t, mask1, mask2, mask3, mask4` — p.89
- `CROOF_` — `CROOF_ top_material, bottom_material, side_material, n, xb, yb, xe, ye, height, angle, thickness, x1, y1, alpha1, s1, ...` — p.89
- `CROOF_{2}` — `CROOF_{2} top_material, bottom_material, side_material, n, xb, yb, xe, ye, height, angle, thickness, x1, y1, alpha1, s1, mat1, ...` — p.92
- `CROOF_{3}` — `CROOF_{3} top_material, bottom_material, side_material, mask, n, xb, yb, xe, ye, height, angle, thickness, x1, y1, alpha1, s1, mat1, ...` — p.93
- `CROOF_{4}` — `CROOF_{4} top_material, bottom_material, side_material, mask, n, xb, yb, xe, ye, height, angle, thickness, x1, y1, alpha1, s1, mat1, ...` — p.94
- `MESH` — `MESH a, b, m, n, mask, z11, z12, ..., z1m, z21, z22, ..., z2m, ...` — p.94
- `ARMC` — `ARMC r1, r2, l, h, d, alpha` — p.96
- `ARME` — `ARME l, r1, r2, h, d` — p.97
- `ELBOW` — `ELBOW r1, alpha, r2` — p.98

### Planar Shapes in 3D

- `HOTSPOT` — `HOTSPOT x, y, z [, unID [, paramReference [, flags [, displayParam [, customDescription]]]]]` — p.99
- `HOTLINE` — `HOTLINE x1, y1, z1, x2, y2, z2, unID` — p.99
- `HOTARC` — `HOTARC r, alpha, beta, unID` — p.100
- `LIN_` — `LIN_ x1, y1, z1, x2, y2, z2` — p.100
- `RECT` — `RECT a, b` — p.100
- `POLY` — `POLY n, x1, y1, ..., xn, yn` — p.100
- `POLY_` — `POLY_ n, x1, y1, s1, ..., xn, yn, sn` — p.101
- `PLANE` — `PLANE n, x1, y1, z1, ..., xn, yn, zn` — p.102
- `PLANE_` — `PLANE_ n, x1, y1, z1, s1, ..., xn, yn, zn, sn` — p.102
- `CIRCLE` — `CIRCLE r` — p.102
- `ARC` — `ARC r, alpha, beta` — p.103

### Shapes Generated from Polylines

- `EXTRUDE` — `EXTRUDE n, dx, dy, dz, mask, x1, y1, s1, ...` — p.105
- `PYRAMID` — `PYRAMID n, h, mask, x1, y1, s1, ..., xn, yn, sn` — p.108
- `REVOLVE` — `REVOLVE n, alpha, mask, x1, y1, s1, ..., xn, yn, sn` — p.110
- `REVOLVE{2}` — `REVOLVE{2} n, alphaOffset, alpha, mask, sideMat, x1, y1, s1, mat1, ..., xn, yn, sn, matn` — p.115
- `REVOLVE{3}` — `REVOLVE{3} n, alphaOffset, alpha, betaOffset, beta, mask, sideMat, x1, y1, s1, mat1, ..., xn, yn, sn, matn` — p.116
- `REVOLVE{4}` — `REVOLVE{4} n, alphaOffset, alpha, betaOffset, beta, mask, sideMat, x1, y1, s1, mat1, ..., xn, yn, sn, matn` — p.118
- `REVOLVE{5}` — `REVOLVE{5}n, alphaOffset, alpha, betaOffset, beta, mask, sideMat, x1, y1, s1, mat1, ..., xn, yn, sn, matn` — p.118
- `RULED` — `RULED n, mask, u1, v1, s1, ..., un, vn, sn, x1, y1, z1, ..., xn, yn, zn` — p.118
- `RULED{2}` — `RULED{2} n, mask, u1, v1, s1, ..., un, vn, sn, x1, y1, z1, ..., xn, yn, zn` — p.118
- `RULEDSEGMENTED` — `RULEDSEGMENTED n, mask, x11, y11, z11, s1,..., x1n, y1n, z1n, sn, x21, y21, z21, ..., x2n, y2n, z2n` — p.122
- `RULEDSEGMENTED{2}` — `RULEDSEGMENTED{2} top_material, bottom_material, n, mask, textureMode, x11, y11, z11, s1, mat1..., x1n, y1n, z1n, sn, matn, x21, y21, z21, ..., x2n, y2n, z2n` — p.123
- `SWEEP` — `SWEEP n, m, alpha, scale, mask, u1, v1, s1, ..., un, vn, sn, x1, y1, z1, ..., xm, ym, zm` — p.124
- `TUBE` — `TUBE n, m, mask, u1, w1, s1, ...` — p.127
- `TUBE{2}` — `TUBE{2} top_material, bottom_material, cut_material, n, m, mask, u1, w1, s1, mat1, ...` — p.131
- `TUBEA` — `TUBEA n, m, mask, u1, w1, s1, ...` — p.133
- `COONS` — `COONS n, m, mask, x11, y11, z11, ..., x1n, y1n, z1n, x21, y21, z21, ..., x2n, y2n, z2n, x31, y31, z31, ..., x3m, y3m, z3m, x41, y41, z41, ..., x4m, y4m, z4m` — p.136
- `COONS{2}` — `COONS{2} n, m, mask, x11, y11, z11, ..., x1n, y1n, z1n, x21, y21, z21, ..., x2n, y2n, z2n, x31, y31, z31, ..., x3m, y3m, z3m, x41, y41, z41, ..., x4m, y4m, z4m` — p.139
- `MASS` — `MASS top_material, bottom_material, side_material, n, m, mask, h, x1, y1, z1, s1, ...` — p.139
- `MASS{2}` — `MASS{2} top_material, bottom_material, side_material, n, m, mask, h, x1, y1, z1, s1, ...` — p.142
- `POLYROOF` — `POLYROOF defaultMat, k, m, n, offset, thickness, applyContourInsidePivot, z_1, ..., z_k, pivotX_1, pivotY_1, pivotMask_1, roofAngle_11, gableOverhang_11, topMat_11, bottomMat_11, ...` — p.143
- `POLYROOF{2}` — `POLYROOF{2} defaultMat, k, m, n, offset, thickness, totalThickness, applyContourInsidePivot, z_1, ..., z_k, pivotX_1, pivotY_1, pivotMask_1, roofAngle_11, gableOverhang_11, topMat_11, bottomMat_11, ...` — p.148
- `POLYROOF{3}` — `POLYROOF{3} defaultMat, mask, k, m, n, offset, thickness, totalThickness, applyContourInsidePivot, z_1, ..., z_k, pivotX_1, pivotY_1, pivotMask_1, roofAngle_11, gableOverhang_11, topMat_11, bottomMat_11, ...` — p.148
- `POLYROOF{4}` — `POLYROOF{4} defaultMat, mask, k, m, n, offset, thickness, totalThickness, applyContourInsidePivot, z_1, ..., z_k, pivotX_1, pivotY_1, pivotMask_1, roofAngle_11, gableOverhang_11, topMat_11, bottomMat_11, ...` — p.151
- `EXTRUDEDSHELL` — `EXTRUDEDSHELL topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, offset, thickness, flipped, trimmingBody, x_tb, y_tb, x_te, y_te, topz, tangle, x_bb, y_bb, x_be, y_be, bottomz, bangle, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.151
- `EXTRUDEDSHELL{2}` — `EXTRUDEDSHELL{2} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, x_tb, y_tb, x_te, y_te, topz, tangle, x_bb, y_bb, x_be, y_be, bottomz, bangle,` — p.152
- `EXTRUDEDSHELL{3}` — `EXTRUDEDSHELL{3} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, x_tb, y_tb, x_te, y_te, topz, tangle, x_bb, y_bb, x_be, y_be, bottomz, bangle,` — p.154
- `REVOLVEDSHELL` — `REVOLVEDSHELL topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.154
- `REVOLVEDSHELL{2}` — `REVOLVEDSHELL{2} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.155
- `REVOLVEDSHELL{3}` — `REVOLVEDSHELL{3} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.157
- `REVOLVEDSHELLANGULAR` — `REVOLVEDSHELLANGULAR topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, segmentationType, nOfSegments, preThickenTran_11, preThickenTran_12, preThickenTran_13,` — p.157
- `REVOLVEDSHELLANGULAR{2}` — `REVOLVEDSHELLANGULAR{2} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, segmentationType, nOfSegments, preThickenTran_11, preThickenTran_12, preThickenTran_13,` — p.158
- `REVOLVEDSHELLANGULAR{3}` — `REVOLVEDSHELLANGULAR{3} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, status, offset, thickness, flipped, trimmingBody, alphaOffset, alpha, segmentationType, nOfSegments, preThickenTran_11, preThickenTran_12, preThickenTran_13,` — p.158
- `RULEDSHELL` — `RULEDSHELL topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, m, g, offset, thickness, flipped, trimmingBody, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14, preThickenTran_21, preThickenTran_22, preThickenTran_23, preThickenTran_24,` — p.159
- `RULEDSHELL{2}` — `RULEDSHELL{2} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, m, g, status, offset, thickness, flipped, trimmingBody, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.161
- `RULEDSHELL{3}` — `RULEDSHELL{3} topMat, bottomMat, sideMat_1, sideMat_2, sideMat_3, sideMat_4, defaultMat, n, m, g, status, offset, thickness, flipped, trimmingBody, preThickenTran_11, preThickenTran_12, preThickenTran_13, preThickenTran_14,` — p.164

### Elements for Visualization

- `LIGHT` — `LIGHT red, green, blue, shadow, radius, alpha, beta, angle_falloff, distance1, distance2, distance_falloff [[,] ADDITIONAL_DATA name1 = value1, name2 = value2, ...]` — p.164
- `PICTURE` — `PICTURE expression, a, b, mask` — p.169

### 3D Text Elements

- `TEXT` — `TEXT d, 0, expression` — p.170
- `RICHTEXT` — `RICHTEXT x, y, height, 0, textblock_name` — p.171

### Primitive Elements

- `VERT` — `VERT x, y, z` — p.172
- `VERT{2}` — `VERT x, y, z, hard` — p.172
- `TEVE` — `TEVE x, y, z, u, v` — p.173
- `VECT` — `VECT x, y, z` — p.173
- `EDGE` — `EDGE vert1, vert2, pgon1, pgon2, status` — p.173
- `PGON` — `PGON n, vect, status, edge1, edge2, ..., edgen` — p.174
- `PGON{2}` — `PGON{2} n, vect, status, wrap, edge_or_wrap1, ..., edge_or_wrapn` — p.175
- `PGON{3}` — `PGON{3} n, vect, status, wrap_method, wrap_flags, edge_or_wrap1, ..., edge_or_wrapn` — p.175
- `PIPG` — `PIPG expression, a, b, mask, n, vect, status, edge1, edge2, ..., edgen` — p.175
- `COOR` — `COOR wrap, vert1, vert2, vert3, vert4` — p.175
- `COOR{2}` — `COOR{2} wrap_method, wrap_flags, vert1, vert2, vert3, vert4` — p.177
- `COOR{3}` — `COOR{3} wrapping_method, wrap_flags, origin_X, origin_Y, origin_Z, endOfX_X, endOfX_Y, endOfX_Z, endOfY_X, endOfY_Y, endOfY_Z, endOfZ_X, endOfZ_Y, endOfZ_Z` — p.178
- `BODY` — `BODY status` — p.180
- `BASE` — `BASE` — p.183

### NURBS Primitive Elements

- NURBS Face trimming — p.185
- NURBS Geometry Commands — p.185
- NURBS Topology Commands — p.187

### Point Clouds

- `POINTCLOUD` — `POINTCLOUD "data_file_name"` — p.192

### Cutting in 3D

- `CUTPLANE` — `CUTPLANE [x [, y [, z [, side [, status]]]]] [statement1 ... statementn]` — p.193
- `CUTPLANE{2}` — `CUTPLANE{2} angle [, status] [statement1 ... statementn]` — p.193
- `CUTPLANE{3}` — `CUTPLANE{3} [x [, y [, z [, side [, status]]]]] [statement1 ... statementn]` — p.193
- `CUTPOLY` — `CUTPOLY n, x1, y1, ..., xn, yn [, x, y, z] [statement1` — p.197
- `CUTPOLYA` — `CUTPOLYA n, status, d, x1, y1, mask1, ..., xn, yn, maskn [, x, y, z] [statement1` — p.199
- `CUTSHAPE` — `CUTSHAPE d [, status] [statement1 statement2 ... statementn]` — p.202
- `CUTFORM` — `CUTFORM n, method, status, rx, ry, rz, d, x1, y1, mask1 [, mat1], ...` — p.202
- `CUTFORM{2}` — `CUTFORM{2} n, method, status, rx, ry, rz, d, x1, y1, mask1 [, mat1], ...` — p.204

### Solid Geometry Commands

- `GROUP - ENDGROUP` — `GROUP "name" [statement1 ... statementn]` — p.208
- `ADDGROUP` — `ADDGROUP (g_expr1, g_expr2)` — p.209
- `SUBGROUP` — `SUBGROUP (g_expr1, g_expr2)` — p.209
- `ISECTGROUP` — `ISECTGROUP (g_expr1, g_expr2)` — p.209
- `ISECTLINES` — `ISECTLINES (g_expr1, g_expr2)` — p.210
- `PLACEGROUP` — `PLACEGROUP g_expr` — p.210
- `KILLGROUP` — `KILLGROUP g_expr` — p.210
- `SWEEPGROUP` — `SWEEPGROUP (g_expr, x, y, z)` — p.211
- `CREATEGROUPWITHMATERIAL` — `CREATEGROUPWITHMATERIAL (g_expr, repl_directive, pen, material)` — p.213

### Binary 3D

- `BINARY` — `BINARY mode [, section, elementID]` — p.213

## 2D Shapes


### Drawing Elements

- `HOTSPOT2` — `HOTSPOT2 x, y [, unID [, paramReference [, flags [, displayParam [, "customDescription"]]]]]` — p.215
- `HOTLINE2` — `HOTLINE2 x1, y1, x2, y2, unID` — p.215
- `HOTARC2` — `HOTARC2 x, y, r, startangle, endangle, unID` — p.216
- `LINE2` — `LINE2 x1, y1, x2, y2` — p.216
- `RECT2` — `RECT2 x1, y1, x2, y2` — p.216
- `POLY2` — `POLY2 n, frame_fill, x1, y1, ..., xn, yn` — p.216
- `POLY2_` — `POLY2_ n, frame_fill, x1, y1, s1, ..., xn, yn, sn` — p.217
- `POLY2_A` — `POLY2_A n, frame_fill, fill_pen, x1, y1, s1, ..., xn, yn, sn` — p.218
- `POLY2_B` — `POLY2_B n, frame_fill, fill_pen, fill_background_pen, x1, y1, s1, ..., xn, yn, sn` — p.219
- `POLY2_B{2}` — `POLY2_B{2} n, frame_fill, fill_pen, fill_background_pen, fillOrigoX, fillOrigoY, fillAngle, x1, y1, s1, ..., xn, yn, sn` — p.219
- `POLY2_B{3}` — `POLY2_B{3} n, frame_fill, fill_pen, fill_background_pen, fillOrigoX, fillOrigoY, mxx, mxy, myx, myy, x1, y1, s1, ..., xn, yn, sn` — p.220
- `POLY2_B{4}` — `POLY2_B{4} n, frame_fill, fill_pen, fill_background_pen, fillOrigoX, fillOrigoY, mxx, mxy, myx, myy, gradientInnerRadius, x1, y1, s1, ..., xn, yn, sn` — p.220
- `POLY2_B{5}` — `POLY2_B{5} n, frame_fill, fillcategory, distortion_flags, fill_pen, fill_background_pen, fillOrigoX, fillOrigoY, mxx, mxy, myx, myy, gradientInnerRadius, x1, y1, s1, ..., xn, yn, sn` — p.220
- `POLY2_B{6}` — `POLY2_B{6} n, frame_fill, fillcategory, distortion_flags, fill_pen, fill_background_pen, fillOrigoX, fillOrigoY, mxx, mxy, myx, myy, gradientInnerRadius, x1, y1, s1, pen1, linetype1, ..., xn, yn, sn, penn, linetypen` — p.221
- `ARC2` — `ARC2 x, y, r, alpha, beta` — p.222
- `CIRCLE2` — `CIRCLE2 x, y, r` — p.222
- `SPLINE2` — `SPLINE2 n, status, x1, y1, angle1, ..., xn, yn, anglen` — p.223
- `SPLINE2A` — `SPLINE2A n, status, x1, y1, angle1, length_previous1, length_next1, ...` — p.224
- `PICTURE2` — `PICTURE2 expression, a, b, mask` — p.226
- `PICTURE2{2}` — `PICTURE2{2} expression, a, b, mask` — p.226

### Text Element

- `TEXT2` — `TEXT2 x, y, expression` — p.226
- `RICHTEXT2` — `RICHTEXT2 x, y, textblock_name` — p.227

### Binary 2D

- `FRAGMENT2` — `FRAGMENT2 fragment_index, use_current_attributes_flag` — p.227

### 3D Projections in 2D

- `PROJECT2` — `PROJECT2 projection_code, angle, method` — p.227
- `PROJECT2{2}` — `PROJECT2{2} projection_code, angle, method [, backgroundColor, fillOrigoX, fillOrigoY, filldirection]` — p.228
- `PROJECT2{3}` — `PROJECT2{3} projection_code, angle, method, parts [, backgroundColor, fillOrigoX, fillOrigoY, filldirection][[,]` — p.231
- `PROJECT2{4}` — `PROJECT2{4} projection_code, angle, useTransparency, statusParts, numCutplanes, cutplaneHeight1, ..., cutplaneHeightn, method1, parts1, cutFillIndex1, cutFillFgPen1, cutFillBgPen1, cutFillOrigoX1, cutFillOrigoY1, cutFillDirection1,` — p.232

### Drawings in the List

- `DRAWING2` — `DRAWING2 [expression]` — p.235
- `DRAWING3` — `DRAWING3 projection_code, angle, method` — p.235
- `DRAWING3{2}` — `DRAWING3{2} projection_code, angle, method [, backgroundColor, fillOrigoX, fillOrigoY, filldirection]` — p.235
- `DRAWING3{3}` — `DRAWING3{3} projection_code, angle, method, parts [, backgroundColor, fillOrigoX, fillOrigoY, filldirection][[,]` — p.235

## Status Codes


### Additional Status Codes

- Previous part of the polyline: current position and tangent is defined — p.247
- Segment by absolute endpoint — p.247
- Segment by relative endpoint — p.247
- Segment by length and direction — p.248
- Tangential segment by length — p.248
- Set start point — p.249
- Close polyline — p.249
- Set tangent — p.249
- Set centerpoint — p.250
- Tangential arc to endpoint — p.250
- Tangential arc by radius and angle — p.251
- Arc using centerpoint and point on the final radius — p.251
- Arc using centerpoint and angle — p.252
- Full circle using centerpoint and radius — p.252

## Attributes


### Directives

- Directives for 3D and 2D Scripts — p.258
- Directives Used in 3D Scripts Only — p.262
- Directives Used in 2D Scripts Only — p.267

### Directives (extracted from the Attributes chapter, not separate TOC entries)

- `LET` — `[LET] varnam = n` — p.258
- `RADIUS` — `RADIUS radius_min, radius_max` — p.258
- `RESOL` — `RESOL n` — p.259
- `TOLER` — `TOLER d` — p.260
- `PEN` — `PEN n` — p.261
- `LINE_PROPERTY` — `LINE_PROPERTY expr` — p.262
- `STYLE` — `[SET] STYLE name_string` — p.262
- `MODEL` — `MODEL WIRE` — p.262
- `MATERIAL` — `[SET] MATERIAL name_or_index` — p.263
- `BUILDING_MATERIAL` — `[SET] BUILDING_MATERIAL name_or_index` — p.264
- `SECT_FILL` — `SECT_FILL fill, fill_background_pen,` — p.265
- `SECT_ATTRS` — `SECT_ATTRS fill, fill_background_pen,` — p.265
- `SECT_ATTRS{2}` — `SECT_ATTRS{2} contour_pen [, line_type]` — p.265
- `SHADOW` — `SHADOW casting [, catching]` — p.265
- `DRAWINDEX` — `DRAWINDEX number` — p.267
- `FILL` — `[SET] FILL name_string` — p.267
- `LINE_TYPE` — `[SET] LINE_TYPE name_string` — p.267
- `PARAGRAPH` — `PARAGRAPH name alignment, firstline_indent,` — p.285
- `TEXTBLOCK` — `TEXTBLOCK name width, anchor, angle, width_factor, charspace_factor, fixed_height,` — p.286
- `TEXTBLOCK_` — `TEXTBLOCK_ name width, anchor, angle, width_factor, charspace_factor, fixed_height, n,` — p.287
- `FILE_DEPENDENCE` — `FILE_DEPENDENCE "name1" [, "name2", ...]` — p.288

### Inline Attribute Definition

- Materials — p.268
- Fills — p.274
- Line Types — p.282
- Text Styles and Text Blocks — p.283
- Additional Data — p.287

### External file dependence

- `FILE_DEPENDENCE` — `FILE_DEPENDENCE "name1" [, "name2", ...]` — p.288

## Non-Geometric Scripts


### The Properties Script

- `DATABASE_SET` — `DATABASE_SET set_name [, descriptor_name, component_name, unit_name, key_name, criteria_name, list_set_name]` — p.289
- `DESCRIPTOR` — `DESCRIPTOR name [, code, keycode]` — p.290
- `REF DESCRIPTOR` — `REF DESCRIPTOR code [, keycode]` — p.290
- `COMPONENT` — `COMPONENT name, quantity, unit [, proportional_with, code, keycode, unitcode]` — p.290
- `REF COMPONENT` — `REF COMPONENT code [, keycode [, numeric_expression]]` — p.291
- `BINARYPROP` — `BINARYPROP` — p.291
- `SURFACE3D` — `SURFACE3D ()` — p.291
- `VOLUME3D` — `VOLUME3D ()` — p.291
- `POSITION` — `POSITION position_keyword` — p.291
- `DRAWING` — `DRAWING` — p.292

### The Parameter Script

- `VALUES` — `VALUES "parameter_name" [,]value_definition1 [, value_definition2, ...]` — p.293
- `VALUES{2}` — `VALUES{2} "parameter_name" [,]num_expression1, description1, [, num_expression2, description2, ...]` — p.294
- `PARAMETERS` — `PARAMETERS name1 = expression1 [, name2 = expression2, ..., namen = expressionn]` — p.295
- `LOCK` — `LOCK "name1" [, "name2", ..., "namen"]` — p.295
- `HIDEPARAMETER` — `HIDEPARAMETER "name1" [, "name2", ..., "namen"]` — p.296

### The User Interface Script

- `UI_DIALOG` — `UI_DIALOG title [, size_x, size_y]` — p.297
- `UI_PAGE` — `UI_PAGE page_number [, parent_id, page_title [, image]]` — p.297
- `UI_CURRENT_PAGE` — `UI_CURRENT_PAGE index` — p.298
- `UI_BUTTON` — `UI_BUTTON type, text, x, y [, width, height, id [, url]]` — p.298
- `UI_PICT_BUTTON` — `UI_PICT_BUTTON type, text, picture_reference, x, y, width, height [, id [, url]]` — p.299
- `UI_SEPARATOR` — `UI_SEPARATOR x1, y1, x2, y2` — p.299
- `UI_GROUPBOX` — `UI_GROUPBOX text, x, y, width, height` — p.299
- `UI_PICT` — `UI_PICT picture_reference, x, y [, width, height [, mask]]` — p.300
- `UI_STYLE` — `UI_STYLE fontsize, face_code` — p.300
- `UI_OUTFIELD` — `UI_OUTFIELD expression, x, y [, width, height [, flags]]` — p.300
- `UI_INFIELD` — `UI_INFIELD "name", x, y, width, height [, method, picture_name, images_number, rows_number, cell_x, cell_y, image_x, image_y, expression_image1, text1, ...` — p.301
- `UI_INFIELD{2}` — `UI_INFIELD{2} name, x, y, width, height [, method, picture_name, images_number, rows_number, cell_x, cell_y, image_x, image_y, expression_image1, text1, ...` — p.301
- `UI_INFIELD{3}` — `UI_INFIELD{3} name, x, y, width, height [, method, picture_name, images_number, rows_number, cell_x, cell_y, image_x, image_y, expression_image1, text1, value_definition1, ... [picIdxArray, textArray, valuesArray,` — p.302
- `UI_INFIELD{4}` — `UI_INFIELD{4} "name", x, y, width, height [, method, picture_name, images_number, rows_number, cell_x, cell_y, image_x, image_y, expression_image1, text1, value_definition1, ... [picIdxArray, textArray, valuesArray,` — p.302
- `UI_CUSTOM_POPUP_INFIELD` — `UI_CUSTOM_POPUP_INFIELD "name", x, y, width, height, storeHiddenId, treeDepth, groupingMethod, selectedValDescription, value1, value2, valuesArray1, .... valuen, valuesArrayn` — p.310
- `UI_CUSTOM_POPUP_INFIELD{2}` — `UI_CUSTOM_POPUP_INFIELD{2} name, x, y, width, height, storeHiddenId, treeDepth, groupingMethod, selectedValDescription, value1, value2, valuesArray1, .... valuen, valuesArrayn` — p.310
- `UI_RADIOBUTTON` — `UI_RADIOBUTTON name, value, text, x, y, width, height` — p.313
- `UI_RADIOBUTTON{2}` — `UI_RADIOBUTTON{2} "name", value, text, x, y, width, height` — p.313
- `UI_PICT_RADIOBUTTON` — `UI_PICT_RADIOBUTTON name, value, text, picture_reference, x, y, width, height [UI_TOOLTIP tooltip]` — p.314
- `UI_PICT_RADIOBUTTON{2}` — `UI_PICT_RADIOBUTTON{2} "name", value, text, picture_reference, x, y, width, height [UI_TOOLTIP tooltip]` — p.314
- `UI_PICT_PUSHCHECKBUTTON` — `UI_PICT_PUSHCHECKBUTTON name, text, picture_reference, frameFlag, x, y, width, height [UI_TOOLTIP tooltip]` — p.314
- `UI_PICT_PUSHCHECKBUTTON{2}` — `UI_PICT_PUSHCHECKBUTTON{2} "name", text, picture_reference, frameFlag, x, y, width, height [UI_TOOLTIP tooltip]` — p.314
- `UI_TEXTSTYLE_INFIELD` — `UI_TEXTSTYLE_INFIELD name, faceCodeMask, x, y, buttonWidth, buttonHeight[, buttonOffsetX]` — p.315
- `UI_TEXTSTYLE_INFIELD{2}` — `UI_TEXTSTYLE_INFIELD{2} "name", faceCodeMask, x, y, buttonWidth, buttonHeight [, buttonOffsetX]` — p.315
- `UI_LISTFIELD` — `UI_LISTFIELD fieldID, x, y, width, height [, iconFlag [, description_header [, value_header]]]` — p.316
- `UI_LISTITEM` — `UI_LISTITEM itemID, fieldID, "name" [, childFlag [, image [, paramDesc]]]` — p.316
- `UI_LISTITEM{2}` — `UI_LISTITEM{2} itemID, fieldID, name [, childFlag [, image [, paramDesc]]]` — p.317
- `UI_CUSTOM_POPUP_LISTITEM` — `UI_CUSTOM_POPUP_LISTITEM itemID, fieldID, "name", childFlag, image, paramDesc, storeHiddenId, treeDepth, groupingMethod, selectedValDescription, value1, value2, valuesArray1, .... valuen, valuesArrayn` — p.318
- `UI_CUSTOM_POPUP_LISTITEM{2}` — `UI_CUSTOM_POPUP_LISTITEM{2} itemID, fieldID, name, childFlag, image, paramDesc, storeHiddenId, treeDepth, groupingMethod, selectedValDescription, value1, value2, valuesArray1, .... valuen, valuesArrayn` — p.319
- UI_TOOLTIP — p.321
- `UI_COLORPICKER` — `UI_COLORPICKER "redParamName", "greenParamName", "blueParamName", x0, y0 [, width [, height]]` — p.322
- `UI_COLORPICKER{2}` — `UI_COLORPICKER{2} redParamName, greenParamName, blueParamName, x0, y0 [, width [, height]]` — p.322
- `UI_SLIDER` — `UI_SLIDER "name", x0, y0, width, height [, nSegments [, sliderStyle]]` — p.323
- `UI_SLIDER{2}` — `UI_SLIDER{2} name, x0, y0, width, height [, nSegments [, sliderStyle]]` — p.323

### The Forward Migration Script

- `SETMIGRATIONGUID` — `SETMIGRATIONGUID guid` — p.324
- `STORED_PAR_VALUE` — `STORED_PAR_VALUE ("oldparname", outputvalue)` — p.325
- `DELETED_PAR_VALUE` — `DELETED_PAR_VALUE ("oldparname", outputvalue)` — p.325

### The Backward Migration Script

- `NEWPARAMETER` — `NEWPARAMETER "name", "type" [, dim1 [, dim2]]` — p.327

## Expressions and Functions


### Expressions

- `DICT` — `DICT variableName1[, variableName2...]` — p.328
- `HASKEY` — `HASKEY (dictionary.key)` — p.333
- `REMOVEKEY` — `REMOVEKEY (dictionary.key)` — p.333
- `DIM` — `DIM var1[dim_1], var2[dim_1][dim_2], var3[ ], var4[ ][ ], var5[dim_1][ ], var5[ ][dim_2]` — p.334
- `VARDIM1` — `VARDIM1 (expr)` — p.335
- `VARDIM2` — `VARDIM2 (expr)` — p.335
- `PARVALUE_DESCRIPTION` — `PARVALUE_DESCRIPTION (parname [, ind1 [, ind2]])` — p.338

### Operators

- Arithmetical Operators — p.338
- Relational Operators — p.339
- Boolean Operators — p.339

### Functions

- Arithmetical Functions — p.340
- Circular Functions — p.341
- Transcendental Functions — p.342
- Boolean Functions — p.342
- Statistical Functions — p.342
- Bit Functions — p.343
- `Special Functions` — `Special functions (besides global variables) can be used in the script to communicate with the executing program. They either ask the current` — p.343
- String Functions — p.345

## Control Statements


### Flow Control Statements

- `FOR - TO - NEXT` — `FOR variable_name = initial_value TO end_value [ STEP step_value ] NEXT variable_name` — p.354
- DO - WHILE — p.355
- `WHILE - ENDWHILE` — `WHILE condition DO [statement1` — p.355
- `REPEAT - UNTIL` — `REPEAT [statement1` — p.356
- IF - GOTO — p.357
- IF - THEN - ELSE - ENDIF — p.358
- `GOTO` — `GOTO label` — p.359
- `GOSUB` — `GOSUB label` — p.359
- `RETURN` — `RETURN` — p.359
- `END / EXIT` — `END [v1, v2, ..., vn]` — p.360
- `BREAKPOINT` — `BREAKPOINT expression` — p.360

### Parameter Buffer Manipulation

- `PUT` — `PUT expression [, expression, ...]` — p.361
- `GET` — `GET (n)` — p.361
- `USE` — `USE (n)` — p.361
- `NSP` — `NSP` — p.361

### Macro Objects

- `CALL` — `CALL macro_name_string [,]` — p.364

### Output in an Alert Box or Report Window

- `PRINT` — `PRINT expression [, expression, ...]` — p.366

### File Operations

- `OPEN` — `OPEN (filter, filename, parameter_string)` — p.367
- `INPUT` — `INPUT (channel, recordID, fieldID, variable1 [, variable2, ...])` — p.367
- `VARTYPE` — `VARTYPE (expression)` — p.367
- `OUTPUT` — `OUTPUT channel, recordID, fieldID, expression1 [, expression2, ...]` — p.367
- `CLOSE` — `CLOSE channel` — p.368

### Using Deterministic Add-Ons

- `INITADDONSCOPE` — `INITADDONSCOPE (extension, parameter_string1, parameter_string2)` — p.368
- `PREPAREFUNCTION` — `PREPAREFUNCTION channel, function_name, expression1 [, expression2, ...]` — p.368
- `CALLFUNCTION` — `CALLFUNCTION (channel, function_name, parameter, variable1 [, variable2, ...])` — p.368
- `CLOSEADDONSCOPE` — `CLOSEADDONSCOPE channel` — p.369

## Miscellaneous


### Global Variables

- Script compatibility — p.370
- General environment information — p.371
- Story information — p.376
- Fly-through information — p.376
- General element parameters — p.378
- Object, Lamp, Door, Window, Wall End, Skylight parameters — p.379
- Object, Lamp, Door, Window, Wall End, Skylight, MEP routing parameters — p.379
- Object, Lamp, Door, Window, Wall End, Skylight, Curtain Wall Accessory parameters - available for listing and labels only — p.380
- Object, Lamp, Curtain Wall Accessory parameters - available for listing and labels only — p.380
- Object parameters — p.381
- `Opening parameters - available for listing and labels only` — `OPENING_HEIGHT` — p.381
- `Opening symbol parameters` — `OPENING_SYMBOL_DISPLAY` — p.382
- Window, Door and Wall End parameters — p.386
- Window, Door parameters - available for listing and labels only — p.387
- Lamp parameters - available for listing and labels only — p.388
- `Marker parameters (Detail, Worksheet and Change Markers)` — `MARKER_HEAD_ROT_MODE` — p.388
- `Label parameters` — `LABEL_POSITION` — p.389
- `Wall parameters - available for Doors/Windows, listing and labels` — `WALL_ID` — p.390
- `Wall parameters - available for listing and labels only` — `WALL_LENGTH_A` — p.394
- Column parameters - available for listing and labels only — p.396
- Beam parameters - available for listing and labels only — p.402
- `Slab parameters - available for listing and labels only` — `SLAB_THICKNESS` — p.407
- Stair component parameters — p.410
- Railing component parameters — p.439
- `Roof parameters - available for skylights, listing and labels` — `ROOF_THICKNESS` — p.450
- `Roof parameters - available for listing and labels only` — `ROOF_BOTTOM_SURF` — p.453
- `Fill parameters - available for listing and labels only` — `FILL_LINETYPE` — p.454
- `Mesh parameters - available for listing and labels only` — `MESH_TYPE` — p.455
- Curtain Wall component parameters — p.456
- Curtain Wall parameters - available for listing and labels only — p.458
- Curtain Wall Frame parameters — p.459
- Curtain Wall Panel variables — p.461
- Curtain Wall Panel parameters - available for listing and labels only — p.462
- Curtain Wall Junction parameters - available for listing and labels only — p.462
- Curtain Wall Accessory parameters - available for listing and labels only — p.462
- Migration parameters - available for migration scripts only — p.462
- `Skylight parameters - available for listing and labels only` — `SKYL_MARKER_TXT` — p.463
- Common Parameters for Shells and Roofs - available for listing and labels only — p.463
- Parameters for Morphs - available for listing and labels only — p.468
- Free users’ globals — p.469
- `Example usage of global variables` — `Example: Illustrating the usage of the GLOB_WORLD_ORIGO_... globals` — p.470
- Deprecated Global Variables — p.470

### Fix named optional parameters

- Parameters set by Archicad — p.475
- Parameters set/read by Archicad — p.488
- Parameters read by Archicad — p.490
- Parameters for Curtain Wall — p.496
- Parameters for add-ons — p.502
- Parameters for Text Handling — p.515
- `Parameters for Labels` — `Parameters set or read by Archicad` — p.516
- `Deprecated parameters` — `Deprecated Beam/Column parameters - available for listing and labels only` — p.519

### REQUEST Options

- Request Parameter Script Compatibility — p.521
- Execution context requests — p.530
- Run environment requests — p.533
- `Associated library part requests` — `ASSOCLP_PARVALUE` — p.534
- Story requests — p.536
- `Zone requests` — `ZONE_CATEGORY` — p.537
- MEP requests — p.539
- Dimension formatting requests — p.543
- Working unit formatting requests — p.546
- View Option requests — p.547
- Attribute requests — p.548
- Profile requests — p.553
- Property object requests — p.556
- `Property requests` — `PROPERTIES_OF_PARENT` — p.558
- `Keynote requests` — `KEYNOTE_FOLDER_TREE` — p.567
- Extension requests — p.570
- Deprecated requests — p.571

### Application Query Options

- Document feature — p.572
- MEP System — p.573
- MEP Modeler — p.575
- MEP Connection Type — p.575
- MEP Flexible Segment — p.576
- MEP Bend — p.578
- Parameter Script — p.578
- Core & IFC Properties — p.579
- Library manager — p.580

### Basic Technical Standards

- Introduction — p.581
- Library part format — p.581
- General scripting issues — p.583
- Script type specific issues — p.591
- Writing macros — p.612
- Background Conversion Issues — p.613
- Windows-Macintosh compatibility — p.614

### Coding Standards

- Introduction — p.616
- General — p.616
- Script-related — p.627

### GDL Style Guide

- Introduction — p.638
- Naming Conventions — p.639
- Expressions — p.644
- Flow control statements — p.647
- Subroutines — p.648
- Macro calls — p.650
- Comments — p.650
- Scripts — p.653

### Doors and Windows

- General Guidelines — p.659
- Positioning — p.659
- Creation of Door/Window Library Parts — p.662

### Keywords

- Common Keywords — p.677
- Reserved Keywords — p.680
- 3D Use Only — p.680
- 2D Use Only — p.686
- 2D and 3D Use — p.688
- Non-Geometric Scripts — p.688

### GDL Data I/O Add-On

- Description of Database — p.691
- Opening a Database — p.691
- Reading Values from Database — p.692
- Writing Values into Database — p.693
- `Closing Database` — `CLOSE channel` — p.694

### GDL Datetime Add-On

- Opening Channel — p.694
- Reading Information — p.696
- `Closing Channel` — `CLOSE channel` — p.696

### GDL File Manager I/O Add-On

- Specifying Folder — p.696
- Getting File/Folder Name — p.697
- Finishing Folder Scanning — p.697

### GDL Text I/O Add-On

- Opening File — p.698
- Reading Values — p.699
- Writing Values — p.700
- `Closing File` — `CLOSE channel` — p.700

### Property GDL Add-On

- `Open property database` — `OPEN ("PROP", "database set name", "[database files]")` — p.701
- `Close property database` — `CLOSE (channel_number)` — p.702
- `Input to property database` — `INPUT (channel_number, "query type", "field list", variable1 [, ...])` — p.702
- Output to property database — p.705

### GDL XML Extension

- Opening an XML Document — p.706
- Reading an XML Document — p.707
- Modifying an XML Document — p.711

### Polygon Operations Extension

- Opening a channel — p.715
- Container management — p.716
- Polygon / polyline management — p.716
- Polygon / polyline operation settings — p.719
- Polygon / polyline operations — p.720
- Get resulting polygons / polylines — p.723
- `Closing channel` — `Closes channel "ch". Deletes all of the stored polygons / polylines.` — p.725

### Autotext Guide

- `Project info keywords` — `PROJECTNAME` — p.725
- General — p.727
- `Layout autotexts` — `LAYOUTNAME` — p.727
- `Drawing autotexts` — `DRAWINGNAME` — p.727
- Reference type autotexts — p.728
- `Marker type autotexts` — `MARKERSHEETNUMBER_R` — p.728
- `Change related autotexts` — `CHANGEID` — p.728
- Layout revision related autotexts — p.729

### Built-in Property Guide

- Element-related built-in property IDs — p.729
- Component-related built-in property IDs — p.732

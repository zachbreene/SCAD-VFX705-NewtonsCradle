#######################################
# SP26_VFX705_01_Zach_Breene_NewtonsCradle_v01.py
# VFX705 Assignment 3: Newton's Cradle
# by Zach Breene
# Date Created: 2026-05-08
#######################################

import os

try:
    import maya.cmds as cmds
    import mtoa as ai
    IN_MAYA = True
except ImportError:
    IN_MAYA = False

    class MockCmds:
        def __getattr__(self, name):
            def mock(*args, **kwargs):
                print(f"[MOCK] cmds.{name}({args}, {kwargs})")
                return ["mock_result"]
            return mock

    class MockAi:
        class core:
            @staticmethod
            def createOptions():
                print("[MOCK] ai.core.createOptions()")

    cmds = MockCmds()
    ai = MockAi()


# =====================================================================
# CONSTANTS & SETUP
# =====================================================================

PFX = "zb_"

# Evaluates the HDRI file path. Separated to allow path updates from separate computers.
IN_PATH = r"G:\Q3\VFX705\A3\breene_vfx705_a3\sourceimages"
HDRI_FILE = "empty_play_room_4k.exr"


# =====================================================================
# GUI SETUP
# =====================================================================

# Initializes the main UI window for user input.
def open_ui():
    ui_name = "NewtonsCradleUI"
    
    # Clears existing window instances to prevent duplicates.
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name)
        
    window = cmds.window(ui_name, title="Newton's Cradle Generator", widthHeight=(350, 150))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=15, columnAttach=('both', 15))
    
    cmds.separator(style='none', height=5)
    cmds.text(label="Please Enter a 5 Letter Word (Can Only Be 5 Letters!)", align="center", font="boldLabelFont")
    word_input = cmds.textField(text="HELLO")
    
    cmds.button(label="Generate Newton's Cradle", 
                height=40, 
                backgroundColor=[0.3, 0.5, 0.8], 
                command=lambda x: execute_from_ui(word_input, ui_name)
    )
    
    cmds.showWindow(window)

# Validates UI input and triggers the main scene generation.
def execute_from_ui(word_input, ui_name):
    input_word = cmds.textField(word_input, query=True, text=True)
    cleaned_word = input_word.strip()
    
    # Enforces exactly 5 alphabetical characters to match the pendulum count.
    if len(cleaned_word) == 5 and cleaned_word.isalpha():
        cmds.deleteUI(ui_name) 
        main(cleaned_word.upper()) 
    else:
        cmds.warning("Input must be exactly 5 letters! No numbers or spaces allowed.")


# ============================================================================================================================
# MODELING (NOTE: DONE MOSTLY USING VIBE CODING WITH GOOGLE GEMINI, WITH LARGE AMOUNTS OF NOTETAKING AND FIXING DONE BY HAND)
# ============================================================================================================================

# Wipes previously generated script geometry to ensure a clean scene state.
def cleanup():
    if cmds.objExists(f"{PFX}*"):
        cmds.delete(f"{PFX}*")


def mk_table():
    # =====================================================================
    # zb_Table
    # =====================================================================
    # Generates the base tabletop slab and bevels the primary edges.
    table = cmds.polyCube(w=54.368, h=1, d=37.175, n=f"{PFX}Table")[0]
    cmds.move(0, -0.439, 0, table, absolute=True)
    cmds.polyBevel(table, fraction=0.5, offsetAsFraction=True, segments=5)
    return table


def mk_surge_protector():
    # =====================================================================
    # zb_SurgeProtector Base
    # =====================================================================
    cube = cmds.polyCube(w=1, h=1, d=1, sx=2, sy=2, sz=2, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}SurgeProtector")[0]
    cmds.move(0, 1.111, 0, cube, absolute=True)
    cmds.scale(14.162, 2.236, 6.642, cube, absolute=True)

    # Tapers the base footprint via edge scaling.
    edges_to_scale = [f"{cube}.e[{i}]" for i in [2, 3, 10, 11]]
    cmds.scale(1, 1, 1.033, *edges_to_scale, worldSpace=True, relative=True, pivot=(0, 1.111, 0))

    # Applies progressive bevel iterations to construct the molded plastic shell.
    bevel1_edges = [f"{cube}.e[0:1]", f"{cube}.e[4:5]", f"{cube}.e[8:9]", f"{cube}.e[12:13]"]
    cmds.polyBevel3(*bevel1_edges, fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=7, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    bevel2_ranges = [
        "8:15", "24:32", "36", "39", "42", "45", "48", "51", "54", "56:60", 
        "62:63", "65:70", "74", "78", "81", "84", "87", "90", "93:94", "96:101", 
        "105", "109", "112", "115", "118", "121", "124:125", "127:132", "136", 
        "140", "143", "146", "149", "152", "155"
    ]
    bevel2_edges = [f"{cube}.e[{r}]" for r in bevel2_ranges]
    cmds.polyBevel3(*bevel2_edges, fraction=0.4, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cmds.polyExtrudeFacet(f"{cube}.f[89:96]", constructionHistory=True, keepFacesTogether=True, 
                          pvx=0, pvy=1.111, pvz=0, divisions=1, twist=0, taper=1, off=0, 
                          thickness=0, smoothingAngle=30, localTranslateZ=-0.152)

    # Secondary micro-bevels to catch specular highlights on complex edge intersections.
    bevel3_indices = [
        37, 41, 55, 62, 82, 85, 87, 91, 105, 112, 132, 135, 137, 141, 155, 162, 182, 185, 187, 191, 
        204, 207, 227, 230, 245, 248, 260, 262, 274, 276, 288, 290, 301, 308, 315, 322, 329, 332, 
        339, 346, 353, 360, 372, 379, 386, 393, 400, 402, 409, 416, 423, 430, 442, 449, 456, 463, 
        470, 472, 479, 486, 493, 500, 512, 519, 526, 533, 540, 542, 549, 556, 563, 570
    ]
    bevel3_edges = [f"{cube}.e[{i}]" for i in bevel3_indices]
    cmds.polyBevel3(*bevel3_edges, fraction=0.6, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=4, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    bevel4_ranges = [
        "38", "41", "44", "47", "60", "64", "67", "70", "114", "117", "120", "123", "136", "140", 
        "143", "146", "464", "466", "473:474", "756", "778", "798", "817", "842", "844:846", 
        "872", "874:876", "962", "964:966", "992", "994:996", "1268", "1270", "1276", "1278", 
        "1349", "1359", "1379", "1396"
    ]
    bevel4_edges = [f"{cube}.e[{r}]" for r in bevel4_ranges]
    cmds.polyBevel3(*bevel4_edges, fraction=0.019, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=1, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # Extrudes the main top face cluster to create the raised central plateau.
    cmds.polyExtrudeFacet(f"{cube}.f[704:751]", constructionHistory=True, keepFacesTogether=True, 
                          pvx=0, pvy=1.111, pvz=0, divisions=1, twist=0, taper=1, off=0, 
                          thickness=0, smoothingAngle=30)
    cmds.scale(0.979, 0.979, 0.979, f"{cube}.f[704:751]", worldSpace=True, relative=True, pivot=(0, 1.111, 0))

    center_edge_ranges = [
        "0:31", "1600", "1603:1604", "1607", "1704", "1706:1707", "1767", "1769:1770"
    ]
    center_edges = [f"{cube}.e[{r}]" for r in center_edge_ranges]
    cmds.polyBevel3(*center_edges, fraction=0.560, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # =====================================================================
    # zb_SurgeProtector Booleans
    # =====================================================================
    # Constructs the boolean cutter geometry for the standard 3-prong wall socket.
    plug_cube_1 = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}PlugCube1")[0]
    cmds.move(0.455, 1.603, 0.981, plug_cube_1, absolute=True)
    cmds.scale(0.148, 1.265, 0.725, plug_cube_1, absolute=True)

    plug_cube_2 = cmds.duplicate(plug_cube_1, rr=True, n=f"{PFX}PlugCube2")[0]
    cmds.move(-0.455, 1.603, 0.981, plug_cube_2, absolute=True)

    plug_cyl = cmds.polyCylinder(r=1, h=2, sx=32, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}PlugCyl1")[0]
    cmds.move(0, 1.518, 2.285, plug_cyl, absolute=True)
    cmds.scale(0.431, 0.726, 0.607, plug_cyl, absolute=True)

    cmds.delete(f"{plug_cyl}.f[15:30]", f"{plug_cyl}.f[47:62]", f"{plug_cyl}.f[79:94]")
    cmds.scale(0.940, 1, 1, f"{plug_cyl}.e[34]", f"{plug_cyl}.e[44]", worldSpace=True, relative=True, pivot=(0, 1.518, 1.948))
    cmds.scale(0.973, 1, 1, f"{plug_cyl}.e[35]", f"{plug_cyl}.e[43]", worldSpace=True, relative=True, pivot=(0, 1.518, 1.856))
    cmds.scale(0.850, 1, 1, f"{plug_cyl}.e[33]", f"{plug_cyl}.e[45]", worldSpace=True, relative=True, pivot=(0, 1.518, 2.053))
    cmds.scale(0.790, 1, 1, f"{plug_cyl}.e[32]", f"{plug_cyl}.e[46]", worldSpace=True, relative=True, pivot=(0, 1.518, 2.167))
    cmds.scale(0.784, 1, 1, f"{plug_cyl}.e[47:48]", worldSpace=True, relative=True, pivot=(0, 1.518, 2.285))
    cmds.delete(f"{plug_cyl}.e[49:63]", f"{plug_cyl}.e[66:80]")
    cmds.polyCloseBorder(f"{plug_cyl}.e[47:52]", ch=True)

    # Duplicates and groups the boolean cutters into a 2x4 grid arrangement.
    base_plug = [plug_cube_1, plug_cube_2, plug_cyl]
    row1_plugs = []
    row1_plugs.extend(base_plug)

    x_offsets = [1.5, 3.0, -1.5, -3.0]
    for offset in x_offsets:
        dupes = cmds.duplicate(base_plug, rr=True)
        cmds.move(offset, 0, 0, dupes, relative=True, worldSpace=True)
        row1_plugs.extend(dupes)

    cmds.move(0, 0, -2.730646, row1_plugs, relative=True, worldSpace=True)

    row2_plugs = cmds.duplicate(row1_plugs, rr=True)
    row2_group = cmds.group(row2_plugs, n=f"{PFX}PlugRow2_Grp")
    
    cmds.xform(row2_group, centerPivots=True)
    cmds.rotate(0, 180, 0, row2_group, relative=True, worldSpace=True)
    cmds.move(0, 0, 2.55, row2_group, relative=True, worldSpace=True)

    # Iterates through the cutter array and runs polyCBoolOp difference operations.
    all_plugs = row1_plugs + row2_plugs
    for p in all_plugs:
        cube = cmds.polyCBoolOp(cube, p, operation=2, constructionHistory=True)[0]

    # Purges history on the complex boolean mesh to preserve scene performance.
    cmds.delete(cube, constructionHistory=True)
    cmds.makeIdentity(cube, apply=True, t=1, r=1, s=1, n=0, pn=1)
    cube = cmds.rename(cube, f"{PFX}SurgeProtector")

    return cube


def mk_plugs():
    # =====================================================================
    # zb_Plug Base
    # =====================================================================
    # Generates the primary adapter block geometry.
    plug = cmds.polyCube(w=1, h=1, d=1, sx=5, sy=5, sz=5, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}Plug")[0]

    cmds.move(-5.220436, 2.995177, 1.558649, plug, absolute=True)
    cmds.scale(1.541044, 1.541044, 1.541044, plug, absolute=True)

    bevel1_ranges = ["100", "105:106", "111:112", "117:118", "123:124", "129", "160", "165:166", "171:172", "177:178", "183:184", "189"]
    bevel1_edges = [f"{plug}.e[{r}]" for r in bevel1_ranges]
    cmds.polyBevel3(*bevel1_edges, fraction=0.3, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    bevel2_ranges = ["16:19", "40:43", "104", "109:110", "115:116", "121:122", "127", "241:244", "315", "319", "322", "325", "328:329", "331:333", "335:336", "338:341", "350", "354", "357", "360", "363"]
    bevel2_edges = [f"{plug}.e[{r}]" for r in bevel2_ranges]
    cmds.polyBevel3(*bevel2_edges, fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=1, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # Manipulates surface topology via edge translations to introduce organic curvature.
    move1_ranges = ["427:428", "431", "434", "437", "440", "444", "449", "452", "455", "458", "461", "463", "468", "471", "475:476", "479", "484:485", "490:491", "496:497", "500", "505", "508:509", "512", "515", "518", "520", "523", "526", "530", "533", "535", "538", "541", "543"]
    move1_edges = [f"{plug}.e[{r}]" for r in move1_ranges]
    cmds.move(0, 0.0456508, 0, *move1_edges, relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.polyBevel3(*move1_edges, fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=1, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    move2_ranges = ["481", "486", "489:490", "493", "496", "499", "502", "506", "511:512", "517", "520", "523", "526", "529", "531", "536:537", "542", "545", "547", "552", "555:556", "559", "564:565", "570:571", "576:577", "580", "585", "588:589", "592", "594", "597", "599"]
    move2_edges = [f"{plug}.e[{r}]" for r in move2_ranges]
    cmds.move(0, 0.0228226, 0, *move2_edges, relative=True, objectSpace=True, worldSpaceDistance=True)

    # Face extrusion creates the USB port socket depth.
    cmds.polyExtrudeFacet(f"{plug}.f[250:289]", constructionHistory=True, keepFacesTogether=True, 
                          divisions=1, twist=0, taper=1, off=0, thickness=0, smoothingAngle=30, 
                          localTranslateZ=-0.012915)

    # =====================================================================
    # zb_USBHolder
    # =====================================================================
    usb_holder = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}USBHolder")[0]

    cmds.move(-5.224, 4.311, 1.566, usb_holder, absolute=True)
    cmds.scale(1.044, 1.110, 0.529, usb_holder, absolute=True)

    cmds.polyBevel3(f"{usb_holder}.e[4:5]", f"{usb_holder}.e[8:9]", fraction=0.1, offsetAsFraction=True, 
                    autoFit=True, depth=1, mitering=0, miterAlong=0, chamfer=True, segments=4, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # =====================================================================
    # zb_WireConnectorBase
    # =====================================================================
    wire_connector = cmds.polyCylinder(r=1, h=2, sx=32, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}WireConnectorBase")[0]

    cmds.move(-5.229, 5.109, 1.562, wire_connector, absolute=True)
    cmds.scale(0.139, 0.252, 0.139, wire_connector, absolute=True)

    # =====================================================================
    # zb_USBLogo
    # =====================================================================
    # Constructs the USB icon via primitive generation and non-linear deformers.
    
    disc_raw = cmds.polyDisc(s=3, sm=4, sd=3, r=1)[0]
    logo_disc1 = cmds.rename(disc_raw, f"{PFX}LogoDisc1")
    cmds.rotate(90, 0, 0, logo_disc1, absolute=True)
    cmds.move(-5.231, 4.561, 1.835, logo_disc1, absolute=True)
    cmds.scale(0.067, 0.067, 0.067, logo_disc1, absolute=True)

    logo_disc2 = cmds.duplicate(logo_disc1, rr=True, n=f"{PFX}LogoDisc2")[0]
    cmds.move(-5.356, 4.314, 1.835, logo_disc2, absolute=True)
    cmds.scale(0.048, 0.048, 0.048, logo_disc2, absolute=True)

    logo_disc3 = cmds.duplicate(logo_disc2, rr=True, n=f"{PFX}LogoDisc3")[0]
    cmds.move(-5.109, 4.241, 1.835, logo_disc3, absolute=True)
    cmds.scale(0.052, 0.052, 0.052, logo_disc3, absolute=True)

    logo_line = cmds.polyPlane(w=1, h=1, sx=1, sy=1, ax=(0, 1, 0), cuv=2, ch=1, n=f"{PFX}LogoLine")[0]
    cmds.rotate(90, 0, 0, logo_line, absolute=True)
    cmds.move(-5.231, 4.322, 1.835, logo_line, absolute=True)
    cmds.scale(0.025, 1.0, 0.406, logo_line, absolute=True)

    logo_arrow = cmds.polyPlane(w=1, h=1, sx=1, sy=1, ax=(0, 1, 0), cuv=2, ch=1, n=f"{PFX}LogoArrow")[0]
    cmds.setAttr(f"{logo_arrow}.rotateX", 90)
    cmds.move(-5.231, 4.078, 1.835, logo_arrow, absolute=True)
    cmds.scale(0.107, 0.107, 0.107, logo_arrow, absolute=True)
    cmds.scale(0.0204638, 1, 1, f"{logo_arrow}.vtx[0:1]", ws=True, r=True, p=(-5.230985, 4.0245, 1.835))

    logo_curveR = cmds.polyPlane(w=1, h=1, sx=10, sy=10, ax=(0, 1, 0), cuv=2, ch=1, n=f"{PFX}LogoCurveR")[0]
    cmds.setAttr(f"{logo_curveR}.translateZ", 1.835)
    cmds.setAttr(f"{logo_curveR}.rotateX", 90)
    cmds.move(0, 0, -3.671125, logo_curveR, r=True, os=True, wd=True)
    cmds.move(-5.165619, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.528978, logo_curveR, r=True, os=True, wd=True)
    cmds.scale(0.0855691, 1, 1, logo_curveR, ws=True, r=True)
    cmds.scale(1, 0.441293, 1, logo_curveR, ws=True, r=True)
    cmds.move(0, 0, -0.150648, logo_curveR, r=True, os=True, wd=True)
    cmds.move(-0.132185, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.scale(0.455627, 1, 1, logo_curveR, ws=True, r=True)
    cmds.scale(1, 0.504084, 1, logo_curveR, ws=True, r=True)
    cmds.scale(0.92224, 1, 1, logo_curveR, ws=True, r=True)

    # Deforms the plane via bend handle logic to trace the logo's outer spline.
    bend_node, bend_handle = cmds.nonLinear(logo_curveR, type='bend', curvature=153.552689)
    cmds.setAttr(f"{bend_handle}.rotateX", 0)

    # Deletes history to bake the bend deformation, allowing further linear transforms.
    cmds.delete(logo_curveR, constructionHistory=True)
    cmds.rotate(0, 0, -35.468152, logo_curveR, r=True, ws=True, fo=True)
    cmds.scale(0.874633, 0.874633, 0.874633, logo_curveR, ws=True, r=True)
    cmds.move(-0.0324858, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.0259759, logo_curveR, r=True, os=True, wd=True)
    cmds.move(-0.0171537, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.0135888, logo_curveR, r=True, os=True, wd=True)
    cmds.move(0.0220761, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.scale(0.895948, 0.895948, 0.895948, logo_curveR, ws=True, r=True)
    cmds.move(-0.012707, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.rotate(0, 0, -9.594288, logo_curveR, r=True, ws=True, fo=True)
    cmds.move(0, 0, 0.00935909, logo_curveR, r=True, os=True, wd=True)
    cmds.move(0.00511937, 0, 0, logo_curveR, r=True, os=True, wd=True)
    cmds.makeIdentity(logo_curveR, apply=True, t=1, r=1, s=1, n=0, pn=1)

    logo_curveL = cmds.duplicate(logo_curveR, rr=True, n=f"{PFX}LogoCurveL")[0]
    cmds.setAttr(f"{logo_curveL}.scaleX", -1)
    cmds.move(-0.156298, 0, 0, logo_curveL, r=True, os=True, wd=True)
    cmds.move(0, -0.0575941, 0, logo_curveL, r=True, os=True, wd=True)
    cmds.move(-0.00684115, 0, 0, logo_curveL, r=True, os=True, wd=True)

    usb_logo = cmds.group(logo_disc1, logo_disc2, logo_disc3, logo_line, logo_arrow, logo_curveR, logo_curveL, n=f"{PFX}USBLogo")

    # =====================================================================
    # Plug Assembly & Duplication
    # =====================================================================
    all_components = [plug, usb_holder, wire_connector, usb_logo]
    
    cmds.delete(all_components, constructionHistory=True)
    cmds.makeIdentity(all_components, apply=True, t=1, r=1, s=1, n=0, pn=1)

    plug1_grp = cmds.group(*all_components, n=f"{PFX}Plug1")
    cmds.xform(plug1_grp, centerPivots=True)

    # Mirrors the master plug assembly across the Z-axis.
    plug2_grp = cmds.duplicate(plug1_grp, rr=True, n=f"{PFX}Plug2")[0]
    cmds.setAttr(f"{plug2_grp}.scaleZ", -1) 
    cmds.move(0, 0, 3.119345, plug2_grp, relative=True, objectSpace=True, worldSpaceDistance=True)

    plug3_grp = cmds.duplicate(plug2_grp, rr=True, n=f"{PFX}Plug3")[0]
    cmds.move(10.516692, 0, 0, plug3_grp, relative=True, objectSpace=True, worldSpaceDistance=True)

    plug4_grp = cmds.duplicate(plug1_grp, rr=True, n=f"{PFX}Plug4")[0]
    cmds.move(10.516692, 0, 0, plug4_grp, relative=True, objectSpace=True, worldSpaceDistance=True)

    return [plug1_grp, plug2_grp, plug3_grp, plug4_grp]


def mk_wire():
    # =====================================================================
    # zb_PlugWire
    # =====================================================================
    # Initializes the base pipe geometry for the power cables.
    pipe_nodes = cmds.polyPipe(r=1, h=2, t=0.5, sa=20, sh=1, sc=0, ax=(0, 1, 0), cuv=1, rcp=0, ch=1, n=f"{PFX}PlugWire1")
    wire = pipe_nodes[0]          
    wire_history = pipe_nodes[1]  

    cmds.setAttr(f"{wire_history}.subdivisionsAxis", 4)
    cmds.setAttr(f"{wire}.rotateX", 90)
    cmds.setAttr(f"{wire}.rotateZ", 45)
    
    cmds.makeIdentity(wire, apply=True, t=1, r=1, s=1, n=0, pn=1)

    # Removes internal faces to establish hollow topology before bridging endpoints.
    faces_to_del = [f"{wire}.f[{i}]" for i in [2, 6, 10, 14]]
    cmds.delete(*faces_to_del)

    vtx_to_move = [f"{wire}.vtx[{i}]" for i in ["10:11", "14:15"]]
    cmds.move(0, 0.353553, 0, *vtx_to_move, relative=True, objectSpace=True, worldSpaceDistance=True)

    outer_border_edges = [f"{wire}.e[{i}]" for i in [15, 19, 23, 27]]
    cmds.polyCloseBorder(*outer_border_edges, ch=True)
    
    inner_border_edges = [f"{wire}.e[{i}]" for i in [14, 18, 22, 26]]
    cmds.polyCloseBorder(*inner_border_edges, ch=True)

    bevel_edges = [f"{wire}.e[{i}]" for i in ["0:13", "16:17", "20:21", "24:25"]]
    cmds.polyBevel3(*bevel_edges, fraction=0.9, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=6, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cmds.move(0, 4.699762, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 0, 1.41275, wire, r=True, os=True, wd=True)
    cmds.scale(1, 1, 0.573637, wire, ws=True, r=True)
    cmds.scale(0.780794, 1, 1, wire, ws=True, r=True)
    cmds.scale(1, 1, 0.765992, wire, ws=True, r=True)
    cmds.scale(0.797342, 1, 1, wire, ws=True, r=True)
    cmds.scale(1, 1, 0.780965, wire, ws=True, r=True)
    cmds.scale(0.854886, 1, 1, wire, ws=True, r=True)
    cmds.scale(1, 0.693259, 1, wire, ws=True, r=True)
    cmds.scale(0.601527, 0.601527, 0.601527, wire, ws=True, r=True)
    cmds.scale(1, 1, 0.657918, wire, ws=True, r=True)
    cmds.scale(0.944817, 1, 1, wire, ws=True, r=True)
    cmds.scale(1, 1, 0.966107, wire, ws=True, r=True)
    cmds.move(-4.623105, 0, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 1.021555, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 0, 1.177882, wire, r=True, os=True, wd=True)
    cmds.move(-0.634752, 0, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.943377, wire, r=True, os=True, wd=True)
    cmds.move(0.176646, 0, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.0684131, wire, r=True, os=True, wd=True)
    cmds.move(0.0314857, 0, 0, wire, r=True, os=True, wd=True)
    cmds.scale(1.169467, 1.169467, 1.169467, wire, ws=True, r=True)
    cmds.move(0.020154, 0, 0, wire, r=True, os=True, wd=True)
    cmds.move(0, 0, -0.00017113, wire, r=True, os=True, wd=True)
    cmds.scale(1.017867, 1.017867, 1.017867, wire, ws=True, r=True)
    cmds.move(0, -0.365269, 0, wire, r=True, os=True, wd=True)
    cmds.scale(1, 0.668674, 1, wire, ws=True, r=True)
    cmds.move(0, 0.116317, 0, wire, r=True, os=True, wd=True)

    # Scuplts wire curvature via isolated face cluster translations.
    faces_to_move_1_ranges = [
        "0:17", "42:47", "54:59", "72:77", "84:89", "108:113", 
        "122", "125", "128", "131", "134:169", "206:241", 
        "278:313", "350:385"
    ]
    faces_to_move_1 = [f"{wire}.f[{r}]" for r in faces_to_move_1_ranges]
    cmds.move(10.129838, 0, 0, *faces_to_move_1, relative=True, objectSpace=True, worldSpaceDistance=True)

    faces_to_move_2_ranges = [
        "18:23", "48:53", "78:83", "102:107", "120", "123", "126", "129",
        "24", "35", "65", "95", "175:180", "242", "257:261", "314", "329:333", "386", "401:405",
        "25", "34", "64", "94", "174", "181", "193:196", "243", "256", "262", "271:273", "315", "328", "334", "343:345", "387", "400", "406", "415:417",
        "26", "33", "63", "93", "173", "182", "192", "197", "203:204", "244", "255", "263", "270", "274", "277", "316", "327", "335", "342", "346", "349", "388", "399", "407", "414", "418", "421",
        "27", "32", "62", "92", "172", "183", "191", "198", "202", "205", "245", "254", "264", "269", "275:276", "317", "326", "336", "341", "347:348", "389", "398", "408", "413", "419:420",
        "28", "31", "61", "91", "171", "184", "190", "199:201", "246", "253", "265:268", "318", "325", "337:340", "390", "397", "409:412",
        "29:30", "60", "90", "170", "185:189", "247:252", "319:324", "391:396",
        "5", "12", "42", "72", "134", "149:153", "211:216", "283:288", "355:360",
        "4", "13", "43", "73", "135", "148", "154", "163:165", "210", "217", "229:232", "282", "289", "301:304", "354", "361", "373:376",
        "3", "14", "44", "74", "136", "147", "155", "162", "166", "169", "209", "218", "228", "233", "239:240", "281", "290", "300", "305", "311:312", "353", "362", "372", "377", "383:384",
        "2", "15", "45", "75", "137", "146", "156", "161", "167:168", "208", "219", "227", "234", "238", "241", "280", "291", "299", "306", "310", "313", "352", "363", "371", "378", "382", "385",
        "1", "16", "46", "76", "138", "145", "157:160", "207", "220", "226", "235:237", "279", "292", "298", "307:309", "351", "364", "370", "379:381",
        "0", "17", "47", "77", "139:144", "206", "221:225", "278", "293:297", "350", "365:369"
    ]
    
    # Leverages dict.fromkeys to sanitize the list of duplicate face indices generated during complex selections.
    faces_to_move_2_ranges = list(dict.fromkeys(faces_to_move_2_ranges))
    faces_to_move_2 = [f"{wire}.f[{r}]" for r in faces_to_move_2_ranges]

    cmds.move(0, 5.623734, 0, *faces_to_move_2, relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.delete(wire, constructionHistory=True)
    cmds.makeIdentity(wire, apply=True, t=1, r=1, s=1, n=0, pn=1)

    wire2 = cmds.duplicate(wire, rr=True, n=f"{PFX}PlugWire2")[0]
    cmds.move(0, 0, -3.156963, wire2, relative=True, objectSpace=True, worldSpaceDistance=True)

    return [wire, wire2]


def mk_KeyCap(word_to_spell):
    # =====================================================================
    # zb_MasterKeyCapBase
    # =====================================================================
    x_offsets = [-3.0, -1.5, 0.0, 1.5, 3.0]
    assemblies = []
    
    # Instantiates the primary suspension wire geometry.
    cyl_nodes = cmds.polyCylinder(r=1, h=2, sx=20, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}keyWire1")
    key_wire1 = cyl_nodes[0]
    cmds.setAttr(f"{cyl_nodes[1]}.subdivisionsCaps", 0)

    cmds.move(0, 8.239882, 0, key_wire1, r=True, os=True, wd=True)
    cmds.scale(0.100679, 0.100679, 0.100679, key_wire1, ws=True, r=True)
    cmds.move(0, 0, -0.705847, key_wire1, r=True, os=True, wd=True)
    cmds.scale(0.604674, 22.267869, 0.604674, key_wire1, ws=True, r=True)
    cmds.move(0, 0.552124, 0, key_wire1, r=True, os=True, wd=True)
    cmds.scale(0.860966, 0.860966, 0.860966, key_wire1, ws=True, r=True)
    cmds.rotate(-16.698704, 0, 0, key_wire1, r=True, ws=True, fo=True)
    cmds.scale(1, 1.372283, 1, key_wire1, r=True)
    cmds.move(0, 0, -0.128254, key_wire1, r=True, os=True, wd=True)
    cmds.scale(0.808035, 0.765303, 0.808035, key_wire1, r=True)
    cmds.move(0.00845575, 0, 0.00348, key_wire1, r=True, os=True, wd=True)
    cmds.scale(0.93796, 0.93796, 0.93796, key_wire1, r=True)
    cmds.move(-0.00317256, 0, 0, key_wire1, r=True, os=True, wd=True)
    cmds.scale(1, 1.274225, 1, key_wire1, r=True)
    cmds.move(0, 0.15632, 0, key_wire1, r=True, os=True, wd=True)
    cmds.scale(1, 1.033093, 1, key_wire1, r=True)
    cmds.move(0, -0.0331367, 0, key_wire1, r=True, os=True, wd=True)
    cmds.scale(1, 1.016547, 1, key_wire1, r=True)
    cmds.move(0, -0.014686, 0, key_wire1, r=True, os=True, wd=True)
    
    key_wire2 = cmds.duplicate(key_wire1, rr=True, n=f"{PFX}keyWire2")[0]
    cmds.rotate(31.007663, 0, 0, key_wire2, r=True, os=True, fo=True)
    cmds.move(0, 0.452376, 1.53088, key_wire2, r=True, os=True, wd=True) 
    cmds.rotate(5.47349, 0, 0, key_wire2, r=True, os=True, fo=True)
    cmds.move(0, -0.0412737, 0, key_wire2, r=True, os=True, wd=True)
    cmds.rotate(-0.305412, 0, 0, key_wire2, r=True, os=True, fo=True)
    cmds.move(0, 0, 0.00973159, key_wire2, r=True, os=True, wd=True)

    # Generates the primary keycap base block.
    cube_nodes = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}KeycapBase")
    keycap = cube_nodes[0]
    cmds.setAttr(f"{cube_nodes[1]}.subdivisionsWidth", 6)
    
    cmds.move(0, 5.984876, 0, keycap, r=True, os=True, wd=True)
    cmds.scale(1.499856, 1.499856, 1.499856, keycap, r=True) 
    cmds.move(0, -0.0203308, 0, keycap, r=True, os=True, wd=True)

    # Reconfigures the top topology to mimic the specific slant of a mechanical switch key.
    top_faces = [f"{keycap}.f[{i}]" for i in range(6)]
    cmds.scale(0.783777, 0.783777, 0.783777, *top_faces, r=True, p=(4.46992e-08, 5.964545, 0.749928)) 
    cmds.move(0, 0, -0.331358, *top_faces, r=True, os=True, wd=True) 

    cmds.move(0, 0, -0.025781, f"{keycap}.e[27]", r=True, os=True, wd=True)
    cmds.move(0, 0, -0.0226852, f"{keycap}.e[28]", f"{keycap}.e[26]", r=True, os=True, wd=True)
    cmds.move(0, 0, -0.0113258, f"{keycap}.e[29]", f"{keycap}.e[25]", r=True, os=True, wd=True)

    bevel1_edges = [f"{keycap}.e[{i}]" for i in [31, 37, 45, 51]]
    cmds.polyBevel3(*bevel1_edges, fraction=0.5, offsetAsFraction=1, autoFit=1, depth=1, 
                    mitering=0, miterAlong=0, chamfer=1, segments=9, worldSpace=1, 
                    smoothingAngle=30, subdivideNgons=1, mergeVertices=1, mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=1)

    bevel2_indices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 41, 42, 43, 46, 58, 61, 64, 67, 70, 73, 76, 79, 81, 84, 87, 90, 93, 96, 99, 102, 105, 107, 110, 113, 116, 119, 122, 125, 128, 131, 133, 136, 139, 142, 145, 148, 151, 154, 157, 159]
    bevel2_edges = [f"{keycap}.e[{i}]" for i in bevel2_indices]
    cmds.polyBevel3(*bevel2_edges, fraction=0.4, offsetAsFraction=1, autoFit=1, depth=1, 
                    mitering=0, miterAlong=0, chamfer=1, segments=1, worldSpace=1, 
                    smoothingAngle=30, subdivideNgons=1, mergeVertices=1, mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=1)

    # Manipulates bottom faces to construct the female mounting recess for the keyboard switch.
    move_indices = [58, 59, 62, 65, 68, 71, 74, 78, 83, 86, 89, 92, 95, 98, 100, 105, 108, 111, 115, 116, 119, 122, 125, 128, 131, 134, 137, 140, 143, 145, 148, 151, 154, 157, 160, 163, 165, 168, 171, 174, 177, 180, 183, 185, 188, 191, 194, 197, 200, 203]
    move_edges = [f"{keycap}.e[{i}]" for i in move_indices]
    cmds.move(0, 0, 0.148452, *move_edges, r=True, os=True, wd=True)

    scale_indices = [56, 61, 64, 67, 70, 73, 76, 80, 81, 84, 87, 90, 93, 96, 102, 103, 106, 109, 113, 118, 121, 124, 127, 130, 133, 136, 139, 142, 144, 147, 150, 153, 156, 159, 162, 164, 167, 170, 173, 176, 179, 182, 184, 187, 190, 193, 196, 199, 202, 204]
    scale_edges = [f"{keycap}.e[{i}]" for i in scale_indices]
    cmds.scale(1.047056, 1.047056, 1.047056, *scale_edges, r=True, p=(4.46992e-08, 5.964546, -0.749928))
    cmds.move(0, 0, 0.0466755, *scale_edges, r=True, os=True, wd=True)
    cmds.scale(1.00535, 1.00535, 1.00535, *scale_edges, r=True, p=(4.46992e-08, 5.964546, -0.703252))

    bevel3_indices = list(range(10)) + list(range(15, 55))
    bevel3_edges = [f"{keycap}.e[{i}]" for i in bevel3_indices]
    cmds.polyBevel3(*bevel3_edges, fraction=0.2, offsetAsFraction=1, autoFit=1, depth=1, 
                    mitering=0, miterAlong=0, chamfer=1, segments=2, worldSpace=1, 
                    smoothingAngle=30, subdivideNgons=1, mergeVertices=1, mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=1)

    base_components = [key_wire1, key_wire2, keycap]
    master_grp = cmds.group(*base_components, n=f"{PFX}MasterKeyCapBase")

    # =====================================================================
    # Text Generation & Pendulum Assembly Loop
    # =====================================================================
    # Iterates across the 5 input string characters to instantiate unique pendulum assemblies.
    for i in range(5):
        letter = word_to_spell[i]
        offset_x = x_offsets[i]
        grp_name = f"{PFX}NewtonKeyCap{i+1}"
        
        current_grp = cmds.duplicate(master_grp, rr=True, n=grp_name)[0]
        cmds.move(offset_x, 0, 0, current_grp, r=True, os=True, wd=True)

        # Translates char to hex sequence required for Maya's polyType evaluation.
        hex_string = ' '.join([hex(ord(c))[2:].upper() for c in letter])
        
        cmds.CreatePolygonType()
        raw_text_obj = cmds.ls(sl=True)[0]
        letter_obj = cmds.rename(raw_text_obj, f"{PFX}Letter_{letter}_{i+1}")
        
        # Accesses hidden type network nodes to push the evaluated string dynamically.
        hist = cmds.listHistory(letter_obj)
        type_nodes = cmds.ls(hist, type="type")
        extrude_nodes = cmds.ls(hist, type="typeExtrude")
        
        if type_nodes:
            cmds.setAttr(f"{type_nodes[0]}.textInput", hex_string, type="string")
            
        if extrude_nodes:
            cmds.setAttr(f"{extrude_nodes[0]}.extrudeDistance", 0.1) 
            cmds.setAttr(f"{extrude_nodes[0]}.extrudeDivisions", 1)

        cmds.scale(0.06034, 0.06034, 0.06034, letter_obj, r=True)
        cmds.move(-0.303275 + offset_x, 5.64806, 0.407304, letter_obj, r=True, os=True, wd=True)

        cmds.parent(letter_obj, current_grp)
        cmds.xform(current_grp, centerPivots=True)

        # Modifies the scale and rotate pivots to the top of the suspension wires 
        # to properly accommodate expressions driving the Newton's Cradle rotation physics.
        cmds.move(0, 3.014911, 0, f"{current_grp}.scalePivot", f"{current_grp}.rotatePivot", relative=True)

        assemblies.append(current_grp)

    cmds.delete(master_grp)

    return assemblies


def mk_sceneAccessories():
    # =====================================================================
    # zb_SurgeLight
    # =====================================================================
    light = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}SurgeLight")[0]

    cmds.move(6.351364, 2.207754, 0, light, r=True, os=True, wd=True)
    cmds.scale(0.356012, 0.061730, 0.557725, light, r=True)

    bevel1_edges = [f"{light}.e[4:5]", f"{light}.e[8:9]"]
    cmds.polyBevel3(*bevel1_edges, fraction=0.7, offsetAsFraction=1, autoFit=1, depth=1, 
                    mitering=0, miterAlong=0, chamfer=1, segments=7, worldSpace=1, 
                    smoothingAngle=30, subdivideNgons=1, mergeVertices=1, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=1)

    bevel2_indices = [
        1, 2, 3, 4, 18, 21, 24, 27, 30, 33, 36, 38, 41, 44, 47, 50, 53, 56, 59, 61, 
        62, 65, 68, 71, 74, 77, 80, 83, 85, 88, 91, 94, 97, 100, 103, 106
    ]
    bevel2_edges = [f"{light}.e[{i}]" for i in bevel2_indices]
    cmds.polyBevel3(*bevel2_edges, fraction=0.2, offsetAsFraction=1, autoFit=1, depth=1, 
                    mitering=0, miterAlong=0, chamfer=1, segments=7, worldSpace=1, 
                    smoothingAngle=30, subdivideNgons=1, mergeVertices=1, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=1)
    
    # =====================================================================
    # zb_SwitchFrame
    # =====================================================================
    # Instantiates the recessed housing for the main rocker switch.
    pipe_nodes = cmds.polyPipe(r=1, h=2, t=0.5, sa=20, sh=1, sc=0, ax=(0, 1, 0), cuv=1, rcp=0, ch=1, n=f"{PFX}SwitchFrame")
    frame = pipe_nodes[0]
    
    cmds.setAttr(f"{pipe_nodes[1]}.subdivisionsAxis", 4)
    cmds.setAttr(f"{frame}.rotateZ", 90)
    cmds.setAttr(f"{frame}.rotateY", 45)
    
    cmds.move(1.689041, -7.050204, -0.132957, frame, r=True, os=True, wd=True)
    cmds.scale(0.559882, 0.559882, 0.559882, frame, r=True)
    
    cmds.makeIdentity(frame, apply=True, t=1, r=1, s=1, n=0, pn=1)
    
    cmds.scale(0.240078, 1, 2.087883, frame, r=True)
    cmds.move(-0.155110, 0, 0.092947, frame, r=True, os=True, wd=True)
    
    faces = [f"{frame}.f[{i}]" for i in range(4)]
    cmds.scale(1, 1.632907, 1.786635, *faces, r=True, p=(6.895094, 1.100318, -1.195399))
    
    bevel3_indices = list(range(4)) + list(range(12, 16))
    bevel3_edges = [f"{frame}.e[{i}]" for i in bevel3_indices]
    cmds.polyBevel3(*bevel3_edges, fraction=0.2, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # =====================================================================
    # zb_SurgeSwitch
    # =====================================================================
    switch = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=2, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}SurgeSwitch")[0]

    cmds.move(6.825814, 1.098466, -1.195259, switch, absolute=True)
    cmds.scale(0.353127, 0.627600, 1.463813, switch, absolute=True)

    cmds.move(0.169484, 0, 0, f"{switch}.e[13]", relative=True, objectSpace=True, worldSpaceDistance=True)

    bevel4_edges = [f"{switch}.e[{i}]" for i in [7, 9, 11, 13, 15, 17]]
    cmds.polyBevel3(*bevel4_edges, fraction=0.1, offsetAsFraction=True, autoFit=True, depth=-1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=6, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    bevel5_ranges = ["6", "28", "30:33", "35", "52", "54:57", "59", "62", "65:66"]
    bevel5_edges = [f"{switch}.e[{r}]" for r in bevel5_ranges]
    cmds.polyBevel3(*bevel5_edges, fraction=0.01, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=1, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cmds.polyExtrudeFacet(f"{switch}.f[14:29]", constructionHistory=True, keepFacesTogether=True, 
                          pvx=6.826604, pvy=1.098466, pvz=-1.196968, divisions=1, twist=0, taper=1, off=0, 
                          thickness=0, smoothingAngle=30)
    
    cmds.scale(0.980404, 0.980404, 0.980404, f"{switch}.f[14:29]", relative=True, pivot=(6.826604, 1.098466, -1.196968))

    # =====================================================================
    # zb_WireFrame
    # =====================================================================
    wire_frame = cmds.polyCylinder(r=1, h=2, sx=32, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}WireFrame")[0]
    cmds.setAttr(f"{wire_frame}.rotateZ", 90)
    
    cmds.move(6.99665, 1.118336, 1.417752, wire_frame, rpr=True)
    cmds.scale(0.415936, 0.415936, 0.415936, wire_frame, r=True)
    cmds.move(0, 0.368852, 0, wire_frame, r=True, os=True, wd=True)

    bevel6_edges = [f"{wire_frame}.e[{i}]" for i in range(32)]
    cmds.polyBevel3(*bevel6_edges, fraction=0.3, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=7, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    faces_to_del = [f"{wire_frame}.f[{i}]" for i in range(64)]
    cmds.delete(*faces_to_del)

    cmds.polyExtrudeFacet(f"{wire_frame}.f[0:31]", constructionHistory=True, keepFacesTogether=True, 
                          pvx=7.043732, pvy=1.118336, pvz=1.417752, divisions=1, twist=0, taper=1, off=0, 
                          thickness=0, smoothingAngle=30, localTranslateZ=-0.0459289)

    bevel7_indices = [
        7, 10, 25, 34, 43, 52, 61, 70, 79, 88, 97, 106, 115, 124, 133, 142, 151, 160, 
        169, 178, 187, 196, 205, 214, 223, 232, 241, 250, 259, 268, 277, 286
    ]
    bevel7_edges = [f"{wire_frame}.e[{i}]" for i in bevel7_indices]
    cmds.polyBevel3(*bevel7_edges, fraction=0.4, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=4, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # =====================================================================
    # zb_SurgeWire
    # =====================================================================
    surge_wire_nodes = cmds.polyCylinder(r=1, h=2, sx=32, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}SurgeWire")
    surge_wire = surge_wire_nodes[0]
    surge_history = surge_wire_nodes[1]
    
    cmds.setAttr(f"{surge_history}.subdivisionsCaps", 0)
    cmds.setAttr(f"{surge_wire}.rotateZ", 90)
    cmds.move(6.997806, 1.118336, 1.417752, surge_wire, rpr=True)
    cmds.delete(f"{surge_wire}.f[0:31]", f"{surge_wire}.f[33]")
    cmds.xform(surge_wire, centerPivots=True)
    cmds.move(6.997806, 1.118336, 1.417752, surge_wire, rpr=True)
    cmds.scale(0.288586, 0.288586, 0.288586, surge_wire, r=True)

    # Defines an EP curve path for the wire extrusion to trace along the ground plane.
    curve_points = [
        (6.997805, 1.118336, 1.417752), (7.186041, 1.130176, 1.417394),
        (7.562513, 1.153856, 1.416679), (8.107327, 0.507001, 1.422267),
        (9.621174, 0.193173, 1.400392), (9.902655, 0.178856, 1.483537),
        (11.481256, 0.185956, 1.167967), (12.452666, 0.184052, -0.202006),
        (11.406717, 0.184554, -2.535927), (10.118504, 0.184415, -3.033595),
        (9.562732, 0.18448, -4.720957), (12.075729, 0.184351, -5.554732),
        (14.376851, 0.184799, -9.418642), (12.237863, 0.183135, -9.961954),
        (9.453035, 0.189344, -7.517888), (8.30237, 0.228153, -9.693799),
        (10.880671, 0.485758, -10.407672), (10.072949, 0.622147, -11.761888),
        (9.669088, 0.690341, -12.438995)
    ]
    wire_curve = cmds.curve(ep=curve_points, d=3, n=f"{PFX}SurgeWireCurve")

    cmds.polyExtrudeFacet(f"{surge_wire}.f[0]", constructionHistory=True, keepFacesTogether=True, 
                          divisions=150, twist=0, taper=1, off=0, thickness=0, smoothingAngle=30, 
                          inputCurve=wire_curve)

    cmds.delete(surge_wire, constructionHistory=True)
    cmds.makeIdentity(surge_wire, apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.delete(wire_curve)

    # =====================================================================
    # zb_SurgePlug Assembly
    # =====================================================================
    # Generates the terminating wall plug adapter geometry.
    cyl1_nodes = cmds.polyCylinder(r=1, h=2, sx=32, sy=4, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}PlugCylinder")
    plug_cyl = cyl1_nodes[0]
    cmds.setAttr(f"{cyl1_nodes[1]}.subdivisionsCaps", 0)
    
    cmds.move(8.192937, 0.257842, -14.984615, plug_cyl, rpr=True)
    cmds.scale(1.302748, 1.302748, 1.302748, plug_cyl, r=True)
    cmds.scale(1, 0.109033, 1, plug_cyl, r=True)
    cmds.move(0, -0.116037, 0, plug_cyl, r=True, os=True, wd=True)
    cmds.scale(1, 0.811563, 1, plug_cyl, r=True)

    bevel_edges_cyl = [f"{plug_cyl}.e[{i}]" for i in list(range(32)) + list(range(128, 160))]
    cmds.polyBevel3(*bevel_edges_cyl, fraction=0.2, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=4, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cyl2_nodes = cmds.polyCylinder(r=1, h=2, sx=5, sy=2, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1, n=f"{PFX}PlugPentagon")
    plug_pent = cyl2_nodes[0]
    cmds.setAttr(f"{cyl2_nodes[1]}.subdivisionsCaps", 0)
    
    cmds.move(8.216044, 0.211616, -14.972936, plug_pent, r=True, os=True, wd=True)
    cmds.scale(1.036949, 1.036949, 1.036949, plug_pent, r=True)
    cmds.scale(1, 0.526417, 1, plug_pent, r=True)
    cmds.move(0, 0.503048, 0, plug_pent, r=True, os=True, wd=True)
    cmds.move(0, 0.0204666, 0, plug_pent, r=True, os=True, wd=True)
    cmds.scale(1, 0.877913, 1, plug_pent, r=True)

    cmds.move(0, -0.436572, 0, f"{plug_pent}.e[5:9]", r=True, os=True, wd=True)
    
    cmds.polyBevel3(f"{plug_pent}.e[15:24]", fraction=0.2, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cmds.polyExtrudeFacet(f"{plug_pent}.f[0:29]", constructionHistory=True, keepFacesTogether=True, 
                          pvx=8.294600628, pvy=0.2772333916, pvz=-14.97293437, divisions=1, twist=0, taper=1, off=0, 
                          thickness=0, smoothingAngle=30, localTranslateZ=0.0377352)

    bevel2_edges_pent = [f"{plug_pent}.e[{i}]" for i in [126, 132, 137, 142, 147, 154, 160, 165, 170, 175, 182, 188, 193, 198, 203, 210, 216, 221, 226, 231, 238, 244, 249, 254, 259, 261, 263, 265, 267, 269]]
    cmds.polyBevel3(*bevel2_edges_pent, fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    bevel3_ranges_pent = ["5:9", "20", "22:24", "26", "37", "39:41", "43", "54", "56:58", "60", "71", "73:75", "77", "88", "90:92", "94"]
    bevel3_edges_pent = [f"{plug_pent}.e[{r}]" for r in bevel3_ranges_pent]
    cmds.polyBevel3(*bevel3_edges_pent, fraction=0.3, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    cmds.scale(1.138357, 1, 1.221969, plug_pent, r=True)
    cmds.rotate(0, -25.243388, 0, plug_pent, r=True, os=True, fo=True) 
    cmds.scale(1.063691, 1, 1, plug_pent, r=True)
    cmds.move(-0.0314861, 0, 0, plug_pent, r=True, os=True, wd=True)

    # Generates the male contact prongs for the wall socket interface.
    prong_cube = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}PlugProngBase")[0]
    cmds.move(8.64012, 1.901469, -15.349579, prong_cube, r=True, os=True, wd=True)
    cmds.rotate(0, 29.716194, 0, prong_cube, r=True, os=True, fo=True)
    cmds.scale(0.15591, 1, 1, prong_cube, r=True)
    cmds.move(-0.110875, 0, 0, prong_cube, r=True, os=True, wd=True)
    cmds.scale(0.967209, 1, 1, prong_cube, r=True)
    cmds.move(0, 0, -0.297505, prong_cube, r=True, os=True, wd=True)
    cmds.scale(1, 1, 0.657301, prong_cube, r=True)
    cmds.move(0, -0.0449684, 0, prong_cube, r=True, os=True, wd=True)
    cmds.scale(1, 1.352583, 1, prong_cube, r=True)
    cmds.move(0, -0.004456461, 0, prong_cube, r=True, os=True, wd=True)
    cmds.scale(1, 0.989028, 1, prong_cube, r=True)

    cmds.polyBevel3(f"{prong_cube}.e[1:2]", fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    # Executes a boolean difference to bore the structural holes in the prongs.
    bool_cyl = cmds.polyCylinder(r=1, h=2, sx=20, sy=1, sz=1, ax=(0, 1, 0), rcp=0, cuv=3, ch=1)[0]
    cmds.move(0, 0, -11.652396, bool_cyl, r=True, os=True, wd=True)
    cmds.setAttr(f"{bool_cyl}.rotateX", 90)
    cmds.setAttr(f"{bool_cyl}.rotateY", 119.716194)
    cmds.move(0, 7.916525, -1.738853, bool_cyl, r=True, os=True, wd=True)
    cmds.scale(0.463958, 0.463958, 0.463958, bool_cyl, r=True)
    cmds.move(-0.693247, 1.261986, 0, bool_cyl, r=True, os=True, wd=True)
    cmds.scale(0.333708, 0.333708, 0.333708, bool_cyl, r=True)
    cmds.move(-0.0769602, 0, -0.36153435, bool_cyl, r=True, os=True, wd=True)

    prong1 = cmds.polyCBoolOp(prong_cube, bool_cyl, operation=2, constructionHistory=True)[0]
    cmds.delete(prong1, constructionHistory=True)
    cmds.makeIdentity(prong1, apply=True, t=1, r=1, s=1, n=0, pn=1)
    prong1 = cmds.rename(prong1, f"{PFX}PlugProng1")

    prong2 = cmds.duplicate(prong1, rr=True, n=f"{PFX}PlugProng2")[0]
    cmds.move(-0.7897076, 0, 0.44456517, prong2, r=True, os=True, wd=True) 

    # Instantiates the grounding terminal prong.
    circle_prong_nodes = cmds.polyCylinder(r=1, h=2, sx=32, sy=1, sz=1, ax=(0, 1, 0), rcp=1, cuv=3, ch=1, n=f"{PFX}CircleProng")
    circle_prong = circle_prong_nodes[0]
    
    cmds.delete(f"{circle_prong}.f[32:63]")
    cmds.move(8.469898, 2.678254, -14.428439, circle_prong, rpr=True)
    cmds.move(0, -0.695548, 0, circle_prong, r=True, os=True, wd=True)
    cmds.scale(0.234821, 0.234821, 0.234821, circle_prong, r=True)
    cmds.move(0, -0.31773, 0, circle_prong, r=True, os=True, wd=True)
    
    cmds.move(0, -0.162771, 0, f"{circle_prong}.vtx[64]", r=True, os=True, wd=True)
    
    cmds.polyBevel3(f"{circle_prong}.e[32:63]", fraction=0.5, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=6, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)
    
    cmds.move(0, -0.0205041, 0, f"{circle_prong}.vtx[32]", r=True, os=True, wd=True)
    cmds.scale(1, 3.274286, 1, circle_prong, r=True)
    cmds.move(0, 0.075601, 0, circle_prong, r=True, os=True, wd=True)
    cmds.scale(1, 1.022188, 1, circle_prong, r=True)
    
    cmds.move(0, -0.0393568, 0, f"{circle_prong}.vtx[32]", r=True, os=True, wd=True)
    
    bevel_edges_circle = [f"{circle_prong}.e[{i}]" for i in [38, 41, 49, 57, 65, 73, 81, 89, 97, 105, 113, 121, 129, 137, 145, 153, 161, 169, 177, 185, 193, 201, 209, 217, 225, 233, 241, 249, 257, 265, 273, 281]]
    cmds.polyBevel3(*bevel_edges_circle, fraction=0.6, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=4, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    surge_plug_grp = cmds.group(plug_cyl, plug_pent, prong1, prong2, circle_prong, n=f"{PFX}SurgePlug")

    # =====================================================================
    # zb_WireConnectors
    # =====================================================================
    # Generates the strain relief geometry for the cable connections.
    conn_nodes = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=(0, 1, 0), cuv=4, ch=1, n=f"{PFX}WireConnector")
    conn = conn_nodes[0]
    cmds.setAttr(f"{conn_nodes[1]}.subdivisionsWidth", 9)
    
    cmds.rotate(0, -60.975, 0, conn, absolute=True)
    cmds.scale(2.124, 0.757, 1.155, conn, absolute=True)
    cmds.move(9.18, 0.736, -13.146, conn, absolute=True)

    # Iterative edge loop scaling to produce a tapered, conical profile.
    scales_data = [
        ([45,55,65,75], 0.755447, (9.695273, 0.736, -12.217379)),
        ([44,54,64,74], 0.797873, (9.580768, 0.736, -12.423739)),
        ([43,53,63,73], 0.823519, (9.466263, 0.736, -12.630099)),
        ([42,52,62,72], 0.854959, (9.351758, 0.736, -12.83646)),
        ([41,51,61,71], 0.880495, (9.237253, 0.736, -13.04282)),
        ([40,50,60,70], 0.916464, (9.122747, 0.736, -13.24918)),
        ([39,49,59,69], 0.957605, (9.008242, 0.736, -13.455541)),
        ([38,48,58,68], 0.963602, (8.893737, 0.736, -13.661901)),
        ([37,47,57,67], 0.983794, (8.779232, 0.736, -13.868261))
    ]
    for indices, sz, pivot in scales_data:
        edges = [f"{conn}.e[{i}]" for i in indices]
        cmds.scale(1, 1, sz, *edges, relative=True, pivot=pivot)

    conn1 = cmds.duplicate(conn, rr=True, n=f"{PFX}WireConnector1")[0]

    # Deletes alternating face loops to create interlocking, ribbed mesh components.
    del_faces_conn = [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34]
    cmds.delete([f"{conn}.f[{i}]" for i in del_faces_conn])

    del_faces_conn1 = [0, 2, 4, 6, 8, 9, 11, 13, 15, 17, 18, 20, 22, 24, 26, 27, 29, 31, 33, 35, 36, 37]
    cmds.delete([f"{conn1}.f[{i}]" for i in del_faces_conn1])

    conn2 = cmds.duplicate(conn1, rr=True, n=f"{PFX}WireConnector2")[0]
    cmds.scale(1, 1, 0.204295, conn1, relative=True)
    cmds.scale(1, 0.270307, 1, conn2, relative=True)

    # Resolves open manifold geometry resulting from face deletions.
    for i in range(1, 9):
        edges = [f"{conn}.e[{e}]" for e in (20+i, 30+i, 40+i, 50+i)]
        cmds.polyCloseBorder(*edges, ch=True)

    bevel_edges_conn = [f"{conn}.e[{i}]" for i in range(20)]
    cmds.polyBevel3(*bevel_edges_conn, fraction=0.2, offsetAsFraction=True, autoFit=True, depth=1, 
                    mitering=0, miterAlong=0, chamfer=True, segments=5, worldSpace=True, 
                    smoothingAngle=30, subdivideNgons=True, mergeVertices=True, 
                    mergeVertexTolerance=0.0001, miteringAngle=180, angleTolerance=180, ch=True)

    scene_accessories_grp = cmds.group(light, frame, switch, wire_frame, surge_wire, surge_plug_grp, conn, conn1, conn2, n=f"{PFX}SceneAccessories")

    return scene_accessories_grp


# =====================================================================
# ANIMATING WITH EXPRESSIONS
# =====================================================================

# Uses sine wave math to dynamically make the Newton's Cradle rotation physics.
# Uses clamping to simulate directional momentum transfer across the model.
def newton_Animation():
    
    # Generates a continuous -40 to 0 degree rotation for key cap 1.
    cmds.expression(s=f"{PFX}NewtonKeyCap1.rotateZ = clamp(-40, 0, sin(time*5)*-40);", o=f"{PFX}NewtonKeyCap1", n=f"{PFX}Expr_Cap1")
    
    # Adds a small rotation to the negative axis to simulate the cradle impact physics.
    cmds.expression(s=f"{PFX}NewtonKeyCap2.rotateZ = clamp(-5, 0, sin(time*5)*-5);", o=f"{PFX}NewtonKeyCap2", n=f"{PFX}Expr_Cap2")
    
    # Unclamped small sine wave rotation to give continuous small energy transfers to simulate physics in the center geometry.
    cmds.expression(s=f"{PFX}NewtonKeyCap3.rotateZ = sin(time*5)*-3;", o=f"{PFX}NewtonKeyCap3", n=f"{PFX}Expr_Cap3")
    
    # Adds a small rotation to the positive axis to simulate the cradle impact physics.
    cmds.expression(s=f"{PFX}NewtonKeyCap4.rotateZ = clamp(0, 5, sin(time*5)*-5);", o=f"{PFX}NewtonKeyCap4", n=f"{PFX}Expr_Cap4")
    
    # Generates a continuous 0 to 40 degree rotation for key cap 1.
    cmds.expression(s=f"{PFX}NewtonKeyCap5.rotateZ = clamp(0, 40, sin(time*5)*-40);", o=f"{PFX}NewtonKeyCap5", n=f"{PFX}Expr_Cap5")
    
    # Sets the playback timeline to encapsulate the continuous animation cycle.
    cmds.playbackOptions(minTime=1, maxTime=200)


# =====================================================================
# LIGHTING
# =====================================================================

def mk_skydomeLight():
    # Resolves the absolute path for the HDRI environment map.
    full_path = os.path.join(IN_PATH, HDRI_FILE)

    # Instantiates the Arnold Skydome
    skydome_shape = cmds.shadingNode('aiSkyDomeLight', asLight=True, name=f"{PFX}SkydomeLightShape")
    skydome = cmds.rename(skydome_shape, f"{PFX}SkydomeLight")

    # Applies coordinate transformations
    cmds.rotate(-1.849, 193.040, 0.299, skydome, absolute=True)

    # Generates the texture node and connects the HDR environment map.
    image_node = cmds.shadingNode('aiImage', asTexture=True, name=f"{PFX}hdriImage")
    cmds.setAttr(f"{image_node}.filename", full_path, type="string")
    
    # Tells Maya to ignore its default color space rules so we can force it to 'raw' without errors.
    cmds.setAttr(f"{image_node}.ignoreColorSpaceFileRules", 1)
    
    # Bypasses color management to ensure linear evaluation of the raw HDRI data.
    cmds.setAttr(f"{image_node}.colorSpace", "raw", type="string") 
    
    cmds.connectAttr(f"{image_node}.outColor", f"{skydome}.color")
    
    return skydome

def mk_directionalLight():
    # cmds.directionalLight() actually returns the SHAPE node name, not the transform.
    raw_shape = cmds.directionalLight()
    
    # Steps up the hierarchy to grab the transform node so we can rename it properly.
    raw_transform = cmds.listRelatives(raw_shape, parent=True)[0]
    dir_light = cmds.rename(raw_transform, f"{PFX}DirectionalLight")
    
    # Grabs the newly updated shape node name after the rename to safely apply attributes.
    dir_shape = cmds.listRelatives(dir_light, shapes=True)[0]
    
    # Applies coordinate transformations based on provided reference.
    cmds.rotate(-12.222, -22.338, 4.706, dir_light, absolute=True)

    # Configures base intensity.
    cmds.setAttr(f"{dir_shape}.intensity", 3.2)
    
    # Injects Arnold-specific physical attributes directly into the shape node.
    cmds.setAttr(f"{dir_shape}.aiUseColorTemperature", 1)
    cmds.setAttr(f"{dir_shape}.aiColorTemperature", 6600) 
    cmds.setAttr(f"{dir_shape}.aiExposure", 0.500)
    cmds.setAttr(f"{dir_shape}.aiAngle", 3.500)
    cmds.setAttr(f"{dir_shape}.aiSamples", 3)
    cmds.setAttr(f"{dir_shape}.aiShadowDensity", 0.810)
    
    return dir_light


# =====================================================================
# SHADERS
# =====================================================================

def WhiteSiliconeShader():
    shader_name = f"{PFX}WhiteSiliconeShader"
    
    # Checks if Maya already has a shader with this name. If it doesn't, we create a brand new 'aiStandardSurface' shader.
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
         
    # Never use pure 1.0 white in physically based rendering because it reflects more light than exists in real life.
    cmds.setAttr(f"{shader}.baseColor", 0.85, 0.85, 0.85)
    
    # A value of 0.6 makes the reflection very spread out and blurry, giving it a soft, rubbery silicone feel.
    cmds.setAttr(f"{shader}.specularRoughness", 0.6)
    
    # Specular Weight controls how strong the reflections are. Lowered to 0.2 so the rubber doesn't look like shiny plastic.
    cmds.setAttr(f"{shader}.specular", 0.2)

    # Builds a list of the exact objects that need this white silicone shader.
    objs_to_paint = [f"{PFX}SurgeWire", f"{PFX}WireConnector", f"{PFX}WireConnector1", f"{PFX}WireConnector2"]
    
    # Filters the list to make absolutely sure the objects actually exist in the scene before trying to paint them (prevents crashing).
    valid_objs = [obj for obj in objs_to_paint if cmds.objExists(obj)]
    
    # If objects successfully found, select them and hit the 'assign' button in the Hypershade programmatically
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def BlackSiliconeShader():
    shader_name = f"{PFX}BlackSiliconeShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # A very dark gray (0.05). Just like you should avoid pure white, you need to avoid pure 0.0 black because real black objects still reflect some light.
    cmds.setAttr(f"{shader}.baseColor", 0.05, 0.05, 0.05)
    
    cmds.setAttr(f"{shader}.specularRoughness", 0.6)
    cmds.setAttr(f"{shader}.specular", 0.2) 

    # For the black silicone, needs the plug wires and the base connectors. 
    # Because the base connector objects get duplicated inside groups by Maya, their names change slightly.
    # So, this uses 'cmds.ls' with a wildcard '*' to search the entire scene for anything containing that specific name
    objs_to_paint = [f"{PFX}PlugWire1", f"{PFX}PlugWire2"]
    objs_to_paint.extend(cmds.ls(f"*{PFX}WireConnectorBase*", type="transform"))
    
    valid_objs = [obj for obj in objs_to_paint if cmds.objExists(obj)]
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def WhitePlasticGlossyShader():
    shader_name = f"{PFX}WhitePlasticGlossyShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    cmds.setAttr(f"{shader}.baseColor", 0.85, 0.85, 0.85)
    
    # Specular Roughness dropped down to 0.2. A lower number means the reflections are sharper and clearer, giving a glossy plastic finish.
    cmds.setAttr(f"{shader}.specularRoughness", 0.2)
    
    # Specular Weight stays at 1.0 because glossy plastics are highly reflective.
    cmds.setAttr(f"{shader}.specular", 1.0)

    # To find the plugs and holders, this searches for the specific Groups made when vibe coding (Plug1, Plug2, etc).
    # Then it needs to tell Maya to look exactly one step down into that group's hierarchy (teh children).
    # The first child is the Plug base, and the second child is the USBHolder, which I want this shader to attach to.
    valid_objs = []
    for i in range(1, 5):
        grp = f"{PFX}Plug{i}"
        if cmds.objExists(grp):
            children = cmds.listRelatives(grp, children=True, type="transform", fullPath=True)
            if children and len(children) >= 2:
                valid_objs.append(children[0]) # Grabs the main Plug geometry
                valid_objs.append(children[1]) # Grabs the USBHolder geometry
                
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def WhitePlasticShader():
    shader_name = f"{PFX}WhitePlasticShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    cmds.setAttr(f"{shader}.baseColor", 0.85, 0.85, 0.85)
    
    # Specular Roughness set to 0.45. Sits exactly halfway between glossy (0.2) and rubbery (0.6).
    # Tries to mimic a slightly textured, "matte" feel of a standard power strip.
    cmds.setAttr(f"{shader}.specularRoughness", 0.45)
    
    # Drop the overall reflection weight just a bit so it doesn't overpower the scene.
    cmds.setAttr(f"{shader}.specular", 0.5)

    # Unique objects that don't change in name, so we can list them explicitly.
    objs_to_paint = [f"{PFX}SurgeProtector", f"{PFX}SwitchFrame", f"{PFX}SurgeSwitch", f"{PFX}WireFrame", f"{PFX}PlugCylinder", f"{PFX}PlugPentagon"]
    
    valid_objs = [obj for obj in objs_to_paint if cmds.objExists(obj)]
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def BlackPlasticGlossyShader():
    shader_name = f"{PFX}BlackPlasticGlossyShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # Very dark grey, almost black.
    cmds.setAttr(f"{shader}.baseColor", 0.01, 0.01, 0.01)
    
    # Same spec roughness as the white glossy plastic.
    cmds.setAttr(f"{shader}.specularRoughness", 0.2)
    cmds.setAttr(f"{shader}.specular", 1.0)

    # Uses wildcards here to search the entire scene for any geometry node that contains 
    # "LogoDisc", "LogoLine", "LogoArrow", or "LogoCurve" so we can grab all the pieces at once.
    valid_objs = cmds.ls(f"*{PFX}LogoDisc*", f"*{PFX}LogoLine*", f"*{PFX}LogoArrow*", f"*{PFX}LogoCurve*", type="transform")
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def BlackPlasticShader():
    shader_name = f"{PFX}BlackPlasticShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    cmds.setAttr(f"{shader}.baseColor", 0.05, 0.05, 0.05)
    
    # Same spec roughness as the white plastic.
    cmds.setAttr(f"{shader}.specularRoughness", 0.45)
    cmds.setAttr(f"{shader}.specular", 0.5)

    # Searches the scene for anything containing "Letter" in its name.
    valid_objs = cmds.ls(f"*{PFX}Letter*", type="transform")
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def MetalShader():
    shader_name = f"{PFX}MetalShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # Because metalness is 1.0, this color no longer dictates color, but instead what color light is reflected.
    cmds.setAttr(f"{shader}.baseColor", 0.85, 0.85, 0.85)
    
    # Changing metalness to 1.0 tells Arnold to see this shader as true metal.
    cmds.setAttr(f"{shader}.metalness", 1.0)
    
    # Specular Roughness at 0.25 prevents the metal from looking like a fake, perfect mirror.
    cmds.setAttr(f"{shader}.specularRoughness", 0.25)
    cmds.setAttr(f"{shader}.specular", 1.0)
    cmds.setAttr(f"{shader}.base", 1.0)

    # Specific names of the three prongs on the surge plug.
    objs_to_paint = [f"{PFX}PlugProng1", f"{PFX}PlugProng2", f"{PFX}CircleProng"]
    
    valid_objs = [obj for obj in objs_to_paint if cmds.objExists(obj)]
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def GreenLightShader():
    shader_name = f"{PFX}GreenLightShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # Sets the base the light to a dark, dormant green.
    cmds.setAttr(f"{shader}.baseColor", 0.05, 0.2, 0.05)
    
    # Emission Color: This turns the material into a light source. Want it to be green.
    cmds.setAttr(f"{shader}.emissionColor", 0.2, 1.0, 0.2)
    
    # Emission Weight upped to 1.5 so it actively casts green light into the surrounding scene.
    cmds.setAttr(f"{shader}.emission", 1.5)

    valid_objs = [f"{PFX}SurgeLight"]
    
    if cmds.objExists(valid_objs[0]):
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def CopperShader():
    shader_name = f"{PFX}CopperShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # This is the specific RGB ratio that produces a realistic copper reflection.
    cmds.setAttr(f"{shader}.baseColor", 0.95, 0.64, 0.54)
    
    # Metalness Set to 1.0
    cmds.setAttr(f"{shader}.metalness", 1.0)
    
    # Specular Roughness at 0.25 makes the wires shiny but not a mirror shine.
    cmds.setAttr(f"{shader}.specularRoughness", 0.25)
    cmds.setAttr(f"{shader}.specular", 1.0)

    # Uses wildcards to grab all the suspension wires across all the different pendulum letter groups.
    valid_objs = cmds.ls(f"*{PFX}keyWire1*", f"*{PFX}keyWire2*", type="transform")
    
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def PastelBluePlasticShader():
    shader_name = f"{PFX}PastelBluePlasticShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # A cyan/pastel blue RGB ratio.
    cmds.setAttr(f"{shader}.baseColor", 0.4, 0.8, 0.85)
    
    # Specular Roughness at 0.3 is a slightly shiny slightly matte finish.
    cmds.setAttr(f"{shader}.specularRoughness", 0.4)
    cmds.setAttr(f"{shader}.specular", 0.8)

    # Loop through exactly the groups for the 1st and 5th letters.
    # By querying the children of these groups, we know that the 3rd child (index [2]) is always the KeycapBase.
    valid_objs = []
    for i in [1, 5]:
        grp = f"{PFX}NewtonKeyCap{i}"
        if cmds.objExists(grp):
            children = cmds.listRelatives(grp, children=True, type="transform", fullPath=True)
            if children and len(children) >= 3:
                valid_objs.append(children[2]) 
                
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def PastelGreenPlasticShader():
    shader_name = f"{PFX}PastelGreenPlasticShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # A minty pastel green RGB ratio.
    cmds.setAttr(f"{shader}.baseColor", 0.5, 0.85, 0.6)
    cmds.setAttr(f"{shader}.specularRoughness", 0.4)
    cmds.setAttr(f"{shader}.specular", 0.8)

    # Exact same child-targeting logic as the blue keycaps, but looking at the 2nd and 4th letters.
    valid_objs = []
    for i in [2, 4]:
        grp = f"{PFX}NewtonKeyCap{i}"
        if cmds.objExists(grp):
            children = cmds.listRelatives(grp, children=True, type="transform", fullPath=True)
            if children and len(children) >= 3:
                valid_objs.append(children[2]) 
                
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def PastelPurplePlasticShader():
    shader_name = f"{PFX}PastelPurplePlasticShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name
        
    # A light lavender pastel purple RGB ratio.
    cmds.setAttr(f"{shader}.baseColor", 0.7, 0.6, 0.85)
    cmds.setAttr(f"{shader}.specularRoughness", 0.4)
    cmds.setAttr(f"{shader}.specular", 0.8)

    # Exact same child-targeting logic as the other keycaps, but only looking at the dead-center 3rd letter.
    valid_objs = []
    for i in [3]:
        grp = f"{PFX}NewtonKeyCap{i}"
        if cmds.objExists(grp):
            children = cmds.listRelatives(grp, children=True, type="transform", fullPath=True)
            if children and len(children) >= 3:
                valid_objs.append(children[2]) 
                
    if valid_objs:
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


def WoodShader():
    shader_name = f"{PFX}WoodShader"
    
    if not cmds.objExists(shader_name):
        shader = cmds.shadingNode("aiStandardSurface", n=shader_name, asShader=True)
    else:
        shader = shader_name

    # Generates the file texture node to hold the image map.
    file_node_name = f"{PFX}WoodTextureFile"
    if not cmds.objExists(file_node_name):
        file_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True, n=file_node_name)
    else:
        file_node = file_node_name

    # Resolves the absolute path utilizing the global IN_PATH constant setup.
    full_texture_path = os.path.join(IN_PATH, "WoodTexture.png")
    cmds.setAttr(f"{file_node}.fileTextureName", full_texture_path, type="string")

    # Connects the file texture's color output to the material's base color input.
    try:
        cmds.connectAttr(f"{file_node}.outColor", f"{shader}.baseColor", force=True)
    except Exception:
        pass # Silently pass if the connection already exists

    # Physical wood grain is slightly rough, so base specular is increased.
    cmds.setAttr(f"{shader}.specular", 1.0)
    cmds.setAttr(f"{shader}.specularRoughness", 0.45)
    
    # Adding a clear coat layer mimics a polished/varnished tabletop finish.
    cmds.setAttr(f"{shader}.coat", 0.85) 
    cmds.setAttr(f"{shader}.coatRoughness", 0.15) 

    # Selects the table geometry and applies the newly constructed shader network.
    valid_objs = [f"{PFX}Table"]
    
    if cmds.objExists(valid_objs[0]):
        cmds.select(valid_objs, replace=True)
        cmds.hyperShade(assign=shader)


# =====================================================================
# RENDERING
# =====================================================================

def setCamera():
    # Create camera for the scene
    camera = cmds.camera(name=PFX+'myRenderCam')[0]
    cmds.select(camera)
    cmds.move(11.246, 5.961, 21.563, camera)
    cmds.rotate(-1.538, 2544.6, 0, camera)
    cmds.setAttr(f"{camera}.focalLength", 35)  # Set focal length

    # Disable renderability for all cameras except the one we want to render from
    all_cameras = cmds.ls(type='camera')
    for cam in all_cameras:
        cmds.setAttr(f'{cam}.renderable', 0)
    
    # Enable only the desired camera
    cmds.setAttr(f'{camera}.renderable', 1)
    cmds.optionVar(intValue=('renderSequenceAllCameras', 1))

    return camera


def setRenderSettings():
    # Initialize Arnold render settings to ensure the nodes exist in a fresh scene.
    # Wrap this in an IN_MAYA check to avoid errors if testing the code outside the software.
    if IN_MAYA:
        try:
            ai.core.createOptions()
        except Exception as e:
            print(f"Could not load mtoa.core options: {e}")

    # Explicitly set the active renderer in Maya's global settings to Arnold.
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    # Maya uses integer codes for image formats. "51" is the code for "Custom image format".
    # This tells Maya to stop trying to format the image and pass control over to the Arnold Driver.
    cmds.setAttr("defaultRenderGlobals.imageFormat", 51)  
    
    # Explicitly tell the Arnold Driver to process and output the frames in the 'exr' format.
    cmds.setAttr("defaultArnoldDriver.aiTranslator", "exr", type="string") 

    # Turn on sequence animation rendering (1 = true).
    cmds.setAttr("defaultRenderGlobals.animation", 1)
    
    # Set the start frame of our customized render range.
    cmds.setAttr("defaultRenderGlobals.startFrame", 30)
    
    # Set the end frame of our customized render range.
    cmds.setAttr("defaultRenderGlobals.endFrame", 91)
    
    # Set the frame step (rendering every 1 frame to ensure smooth playback).
    cmds.setAttr("defaultRenderGlobals.byFrameStep", 1)

    # Set the specific pixel resolution for a 1080p Full HD render.
    width = 1920
    height = 1080
    cmds.setAttr("defaultResolution.width", width)
    cmds.setAttr("defaultResolution.height", height)
    
    # Calculate and apply the mathematical aspect ratio based on the width and height.
    cmds.setAttr("defaultResolution.deviceAspectRatio", float(width) / height)

    # Assigns the base prefix string for our output files.
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "NewtonsTechCradle", type="string") 
    
    # Sets the number of digits in the frame padding (e.g., a padding of 4 turns frame 30 into '0030').
    cmds.setAttr("defaultRenderGlobals.extensionPadding", 4) 
    
    # Tells Maya to append the frame number to the file name so they aren't overwritten.
    cmds.setAttr("defaultRenderGlobals.useFrameExt", 1) 
    
    # Injects a period between the file name and the frame number (NewtonsTechCradle.0030 instead of NewtonsTechCradle0030)
    cmds.setAttr("defaultRenderGlobals.periodInExt", 1) 
    
    # Ensures the frame number is placed before the actual file extension (NewtonsTechCradle.0030.exr).
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1) 

    # Sets additional Arnold quality settings to improve the final image fidelity.
    if cmds.objExists("defaultArnoldRenderOptions"):
        cmds.setAttr("defaultArnoldRenderOptions.GISpecularSamples", 2)
        cmds.setAttr("defaultArnoldRenderOptions.GISpecularDepth", 2)
    if cmds.objExists("defaultArnoldDriver"):
        cmds.setAttr("defaultArnoldDriver.mergeAOVs", 1)


def renderScene():
    # Triggers the final batch sequence render using all the settings defined in the camera and setRenderSettings blocks.
    cmds.RenderSequence()


# =====================================================================
# MAIN EXECUTION
# =====================================================================

def main(word_to_spell):
    cleanup()
    
    table = mk_table()
    surge_protector = mk_surge_protector()
    plugs = mk_plugs()
    wires = mk_wire()
    keycaps = mk_KeyCap(word_to_spell)
    accessories = mk_sceneAccessories()
    
    # Configures the scene's lighting environment.
    skydome = mk_skydomeLight()
    dir_light = mk_directionalLight()
    
    # Calls all of our custom shader functions sequentially to apply the materials to the geometry.
    WhiteSiliconeShader()
    BlackSiliconeShader()
    WhitePlasticGlossyShader()
    WhitePlasticShader()
    BlackPlasticGlossyShader()
    BlackPlasticShader()
    MetalShader()
    GreenLightShader()
    CopperShader()
    PastelBluePlasticShader()
    PastelGreenPlasticShader()
    PastelPurplePlasticShader()
    WoodShader()
    
    # Establishes the rendering camera for the final shot.
    camera = setCamera()
    
    # Packages everything into a master scene group.
    all_scene_elements = [table, surge_protector] + plugs + wires + keycaps + [accessories, skydome, dir_light, camera]
    cmds.group(*all_scene_elements, n=f"{PFX}scene")
    
    # Executes the expression-based animation logic.
    newton_Animation()
    
    # Clears the active selection so nothing is highlighted during the render.
    cmds.select(clear=True)
    
    # Configures the 1080p, EXR, and frame range settings for the batch render.
    setRenderSettings()
    
    # Triggers the sequence rendering process.
    renderScene()
    
    print(f"Newton's Cradle with '{word_to_spell}' Text generated and rendered successfully!")


if IN_MAYA:
    open_ui()
else:
    print("Code must be run inside Maya.")
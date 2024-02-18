import bpy
import bmesh
import os
import svgwrite
from bpy.app.handlers import persistent
import itertools

class SAVEASSVG_OT_save_face_as_svg(bpy.types.Operator):
    bl_idname = 'saveassvg.save_face_as_svg'
    bl_label = 'Save as SVG'

    @persistent
    def set_filename(self):
        if bpy.data.is_saved:
            print("Absolute path: {}".format(os.path.dirname(bpy.data.filepath)))
            self.filename = "{}".format(os.path.splitext(bpy.data.filepath)[0] + ".svg")
        else:
            self.ShowMessageBox("You need to save the file to a directory before saving to SVG")

    def ShowMessageBox(self, message = "", title = "Save to SVG", icon = 'INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

    def execute(self, context):
        self.set_filename()
        
        dwg = svgwrite.Drawing('{}'.format(self.filename), profile='full')

        drawn = 0
        skipped = 0

        Z = None

        if bpy.context.active_object:
            o = bpy.context.active_object
            if o.mode == 'EDIT' and o.type == "MESH":
                print("{} is a mesh".format(o.name))
                if hasattr(o.data, "transform"):
                        mb = o.matrix_basis
                        o.data.transform(mb)
                m = bmesh.from_edit_mesh(o.data)
                edges = []
                for e in m.edges:
                    if e.select:
                        points = []
                        point1 = e.verts[0]
                        point2 = e.verts[1]
                        if Z is None:
                            Z = point1.co[2]
                            print("Setting Z to export to {}".format(point1.co[2]))
                        if point1.co[2] == Z and point2.co[2] == Z:
                            points.append( (point1.co[0], point1.co[1]) )
                            points.append( (point2.co[0], point2.co[1]) )
                        else:
                            skipped += 1

                        if len(points) > 1:
                            edges.append(points)

                # Have edges in a list, but dupes may exist. Remove the dupes
                edges.sort()
                draw_edges = list(edges for edges,_ in itertools.groupby(edges))

                for edge in draw_edges:
                    drawn += 1
                    print("drawing line between {} and {}) ".format(edge[0], edge[1]))
                    dwg.add(dwg.line(edge[0], edge[1], stroke='black', stroke_width=0.005))
        
        dwg.save()

        print("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))
        self.ShowMessageBox("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))
        return {'FINISHED'}

class SAVEASSVG_OT_select_objects_as_svg(bpy.types.Operator):
    bl_idname = 'saveassvg.save_objects_as_svg'
    bl_label = 'Save as SVG'

    @persistent
    def set_filename(self):
        if bpy.data.is_saved:
            print("Absolute path: {}".format(os.path.dirname(bpy.data.filepath)))
            self.filename = "{}".format(os.path.splitext(bpy.data.filepath)[0] + ".svg")
        else:
            self.ShowMessageBox("You need to save the file to a directory before saving to SVG")

    def ShowMessageBox(self, message = "", title = "Save to SVG", icon = 'INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
 
    def execute(self, context):
        self.set_filename()
        
        dwg = svgwrite.Drawing('{}'.format(self.filename), profile='full')
        black = svgwrite.rgb(100, 100, 100, '%')

        drawn = 0
        skipped = 0
        layers = []

        if len(bpy.context.selected_objects) > 0:
            s = bpy.context.selected_objects
            for o in s:
                Z = None # will be set on first point
                if o.type == "MESH":
                    if hasattr(o.data, "transform"):
                        mb = o.matrix_basis
                        o.data.transform(mb)
                    collection = None
                    if len(o.users_collection) > 0:
                        collection = o.users_collection[0].name
                        if collection not in layers:
                            layers.append(collection)
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.object.mode_set(mode="EDIT")
                    m = bmesh.from_edit_mesh(o.data) 
                    print("{} is a mesh".format(o.name))
                    
                    edges = []
                    print("{} has {} edges".format(o.name, len(m.edges)))
                    for e in m.edges:
                        points = []
                        point1 = e.verts[0]
                        point2 = e.verts[1]
                        if Z is None:
                            Z = point1.co[2]
                            print("Setting Z to export to {}".format(point1.co[2]))
                        if point1.co[2] == Z and point2.co[2] == Z:
                            points.append( (point1.co[0], point1.co[1]) )
                            points.append( (point2.co[0], point2.co[1]) )
                        else:
                            skipped += 1
                            print("Found Z {} on object {}".format(point1.co[2], o.name))

                        if len(points) > 1:
                            edges.append(points)

                    # Have edges in a list, but dupes may exist. Remove the dupes
                    edges.sort()
                    draw_edges = list(edges for edges,_ in itertools.groupby(edges))

                    for edge in draw_edges:
                        drawn += 1
                        print("drawing line between {} and {}) ".format(edge[0], edge[1]))
                        if collection:
                            dwg.add(dwg.line(edge[0], edge[1], stroke='black', stroke_width=0.005))
                        else:
                            dwg.add(dwg.line(edge[0], edge[1], stroke='black', stroke_width=0.005))

                bpy.ops.object.mode_set(mode="OBJECT")
        
        try:
            dwg.save()
            print("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))
            self.ShowMessageBox("Saved {} edges to {}, skipped {} due to difference in Z plane".format(drawn, self.filename, skipped))
        except AttributeError:
            pass

        return {'FINISHED'}

bpy.utils.register_class(SAVEASSVG_OT_save_face_as_svg)
bpy.utils.register_class(SAVEASSVG_OT_select_objects_as_svg)

def face_menu_item_draw_func(self, context):
    self.layout.separator()
    self.layout.operator('saveassvg.save_face_as_svg', icon='DISK_DRIVE')

def selected_menu_item_draw_func(self, context):
    self.layout.separator()
    self.layout.operator('saveassvg.save_objects_as_svg', icon='DISK_DRIVE')
    
bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(face_menu_item_draw_func)
bpy.types.VIEW3D_MT_object_context_menu.append(selected_menu_item_draw_func)

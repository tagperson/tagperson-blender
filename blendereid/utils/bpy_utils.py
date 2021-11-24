import bpy
import import_runtime_mhx2
import makewalk


class SampleOperator(bpy.types.Operator):
    bl_idname = "object.sample_operator"
    bl_label = "Sample Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None


def register_bpy_libs():
    bpy.utils.register_class(SampleOperator)
    import_runtime_mhx2.register()
    makewalk.register()


def remove_object(obj_key = 'Cube'):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.data.objects[obj_key].select_set(True)
    bpy.ops.object.delete()
    if obj_key in bpy.data.meshes:
        mesh = bpy.data.meshes[obj_key]
        bpy.data.meshes.remove(mesh)

def remove_object_v2(obj_key = 'Cube'):
    if obj_key is None:
        return

    # delete obj
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.data.objects[obj_key].select_set(True)
        bpy.ops.object.delete()
    except:
        pass

    # delete mesh
    for mesh_key in bpy.data.meshes.keys():
        if mesh_key.find(obj_key) > -1:
            mesh = bpy.data.meshes[mesh_key]
            print(f"remove meshes {mesh_key}, {mesh}")
            bpy.data.meshes.remove(mesh)


"""
For some reason, the alpha channel in mesh may be incorrect
We need to correct them
"""    
def correct_alpha_channel():
    meshes_keys = bpy.data.meshes.keys()
    for mesh_key in meshes_keys:
        mesh = bpy.data.meshes[mesh_key]
        for material_key in mesh.materials.keys():
            # print(f"material_key={material_key}")
            tree_links = mesh.materials[material_key].node_tree.links
            alpha_links = mesh.materials[material_key].node_tree.nodes['Principled BSDF'].inputs[18].links
            if len(alpha_links) > 0:
                link = alpha_links[0]
                tree_links.remove(link)

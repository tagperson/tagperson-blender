import os
import bpy

def format_mesh_file_name(mesh_id, obj_pose, suffix='mhx2'):
    mesh_file_name = f"{mesh_id}_{obj_pose}.{suffix}"
    return mesh_file_name


def load_object(obj_file_path):
    ext = os.path.splitext(os.path.basename(obj_file_path))[1]
    if ext == '.obj':
        bpy.ops.import_scene.obj(filepath=obj_file_path, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl;")
    elif ext == '.mhx2':
        bpy.ops.import_scene.makehuman_mhx2(filepath=obj_file_path)
    else:
        raise ValueError(f"Unsupported subfix of obj_file_path: {obj_file_path}, only `.obj` and `.mhx2` supported.")


def get_mesh_id(obj_file_path):
    """
    obj_key is `person_05`
    mesh_id is `5`

    """
    pure_name = get_obj_key(obj_file_path)
    mesh_id = int(pure_name.split("_")[0])
    return mesh_id


def get_obj_key(obj_file_path):
    file_name = os.path.basename(obj_file_path)
    pure_name, ext_name = os.path.splitext(file_name)
    if ext_name == '.obj':
        return pure_name
    elif ext_name == '.mhx2':
        return pure_name.lower()
    else:
        return ''

def get_mesh_id_from_obj_name(obj_name):
    mesh_id = int(obj_name.split("_")[0])
    return mesh_id

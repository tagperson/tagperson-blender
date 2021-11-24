import os
import bpy
from tqdm import tqdm
import imageio
import cv2
import numpy as np

from blendereid.utils import bpy_utils, geometry
from blendereid.utils import mesh_utils
from blendereid.core import compositing
from blendereid.core import render_config
from blendereid.core import pose_manager
from blendereid.core import background
from blendereid.core import world_config
from blendereid.schema.attribute import Attribute



def prepare_scene():
    bpy_utils.register_bpy_libs()
    bpy_utils.remove_object(obj_key='Cube')

def prepare_render_setting():
    compositing.compose_render_nodes()
    render_config.setup_basic_render(None)


def compose_gif_file(jpg_file_list, save_path='tmp/ani.gif', fps=5):
    gif_images = []
    for jpg_file in jpg_file_list:
        gif_images.append(imageio.imread(jpg_file))
    imageio.mimsave(save_path, gif_images, fps=fps)
    print(f"gif image save into {save_path}")

def compose_gallery_line_file(jpg_file_list, save_path='tmp/gallery.jpg', target_w=128, target_h=256):
    gallery_np = None
    for jpg_file in jpg_file_list:
        jpg_img = cv2.imread(jpg_file)
        resized_img = cv2.resize(jpg_img, (target_w, target_h))
        gallery_np = np.concatenate((gallery_np, resized_img), axis=1) if gallery_np is not None else resized_img
    cv2.imwrite(save_path, gallery_np)
    print(f"gallery image save into {save_path}")


def load_person_mesh(mesh_path):
    # load and fetch obj for current person
    mesh_utils.load_object(mesh_path)
    obj_key = mesh_utils.get_obj_key(mesh_path)
    obj_person = bpy.data.objects[obj_key]
    # correct alpha for materials to avoid incorrect transparent
    bpy_utils.correct_alpha_channel()

    return obj_key, obj_person


def render_one_person_on_certain_attribute(obj_person, attribute: Attribute, save_path):

    # render option
    camera_distance = attribute.camera_distance
    camera_elev = attribute.camera_elev
    camera_azim = attribute.camera_azim

    # pose
    pose_path = attribute.pose
    if pose_path is not None:
        bpy.ops.mcp.load_pose(filepath=pose_path)
        pose_manager.apply_transform_to_bones(obj_person)
        bpy.context.view_layer.update()

    # background
    img_bg = None if attribute.background is None else bpy.data.images.load(attribute.background)
    background.set_backgound_from_predefined_img(img_bg)


    obj_camera = bpy.data.objects['Camera']
    render = bpy.data.scenes['Scene'].render
    light = bpy.data.objects['Light']

    person_location = (obj_person.location[0], obj_person.location[1], obj_person.location[2])
    obj_camera.location = geometry.calculate_target_location(person_location, camera_distance, camera_azim, camera_elev)


    light_azim = attribute.light_azim
    light_elev = attribute.light_elev
    light_distance = attribute.light_distance
    light.location = geometry.calculate_target_location(obj_person.location, light_distance, light_azim, light_elev)

    bpy.context.view_layer.update()
    
    camera_rotation_euler_x_bias = attribute.cre_x_bias
    camera_rotation_euler_z_bias = attribute.cre_y_bias
    camera_rotation_euler_y_bias = attribute.cre_z_bias
    obj_pose = obj_person.matrix_world.to_translation()
    camera_pos = obj_camera.matrix_world.to_translation()
    direction = obj_pose - camera_pos
    # obj_pose the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    obj_camera.rotation_euler.x += camera_rotation_euler_x_bias
    obj_camera.rotation_euler.z += camera_rotation_euler_z_bias
    obj_camera.rotation_euler.y += camera_rotation_euler_y_bias

    
    render.filepath = save_path

    # render_config.modify_render_config(cfg)
    # image size
    render.resolution_x = attribute.img_width
    render.resolution_y = attribute.img_height
    render.resolution_percentage = 100

    world_config.apply_world_color_frontend(attribute.world_color)
    world_config.apply_color_mask_alpha(attribute.world_color)

    # set gamma
    compositing.set_gamma_value(attribute.gamma_value)

    bpy.ops.render.render(write_still=True)

# render a static image for the person
def render_sample_person(mesh_path, save_path):
    obj_key, obj_person = load_person_mesh(mesh_path)
    
    person_attribute = Attribute(
        mesh_id=None, 
        camera_azim=280, 
        camera_elev=30, 
        camera_distance=30.0, 
        light_azim=280, 
        light_elev=75, 
        light_distance=25.0/1.5, 
        background='data_demo/background_demo/000000000086-1-left.jpg', 
        pose='data_demo/pose_demo/08_04_19.json', 
        camera_idx=-1, 
        img_width=256, 
        img_height=512, 
        partner_exist=False, 
        partner_mesh_id_list=[], 
        cre_x_bias=0.32, 
        cre_y_bias=0.0, 
        cre_z_bias=0.0
    )

    render_one_person_on_certain_attribute(obj_person, person_attribute, save_path=save_path)
    bpy_utils.remove_object_v2(obj_key=obj_key)

# render a gif for different rendering options
def render_sample_person_demo_camera_azim(mesh_path, save_path):
    """
    render a person surround by camera 
    """
    obj_key, obj_person = load_person_mesh(mesh_path)

    person_attribute_list = [Attribute(
        mesh_id=None, 
        camera_azim=camera_azim, 
        camera_elev=30, 
        camera_distance=30.0, 
        light_azim=camera_azim, 
        light_elev=65, 
        light_distance=25.0/1.5, 
        background='data_demo/background_demo/bg_blender_notext.png', 
        pose='data_demo/pose_demo/08_04_19.json', 
        camera_idx=-1, 
        img_width=256, 
        img_height=512, 
        partner_exist=False, 
        partner_mesh_id_list=[], 
        cre_x_bias=0.32, 
        cre_y_bias=0.0, 
        cre_z_bias=0.0
    ) for camera_azim in range(0, 359, 10)]

    save_path_list = [f'tmp/{idx}.jpg' for idx in range(len(person_attribute_list))]
    for idx, p_attr in tqdm(enumerate(person_attribute_list)):
        render_one_person_on_certain_attribute(obj_person, p_attr, save_path=save_path_list[idx])
    compose_gif_file(save_path_list, save_path=save_path, fps=20)

    # remove tmp file
    for tmp_file in save_path_list:
        os.remove(tmp_file)
    bpy_utils.remove_object_v2(obj_key=obj_key)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh_path', type=str, default=None)
    parser.add_argument('--save_path', type=str, default='tmp/sample_person.jpg')
    parser.add_argument('--demo_camera_azim', action="store_true")
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    mesh_path = args.mesh_path
    if mesh_path is None or not os.path.exists(mesh_path):
        raise ValueError(f"Mesh path is not valid: `{mesh_path}`")
    print(f"Render images from {mesh_path}")

    # start
    prepare_scene()
    prepare_render_setting()

    if args.demo_camera_azim:
        if not args.save_path.endswith(".gif"):
            raise ValueError(f"the `save_path` should be `.gif` format when executing the `demo_camera_azim` option...")
        render_sample_person_demo_camera_azim(mesh_path, save_path=args.save_path)
    else:
        render_sample_person(mesh_path, save_path=args.save_path)
    
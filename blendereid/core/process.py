
import os
import bpy
from tqdm import tqdm
import numpy as np
from blendereid.core import background, compositing, camera_config, render_config, pose_manager, world_config, shield, attribute_manager
from blendereid.utils import bpy_utils, mesh_utils, resume_utils, geometry
from blendereid.schema.attribute import Attribute
from blendereid.core import light_config
from blendereid.core import expand

def generate_multiple_persons(cfg):
    # build temp background compositor logic
    compositing.compose_render_nodes()

    if not cfg.BACKGROUND.USE_CAMERA_GROUP:
        img_bg_list = background.load_multiple_bg_imgs(cfg)
    else:
        # NOTE: img_bg_list may be a dict
        img_bg_list = background.load_multiple_bg_imgs_group_by_camera(cfg)

    bg_image_info = None    # cached image -> x,y,percentage info
    if cfg.BACKGROUND.FIX_RESOLUTION_PER_IMAGE.ENABLED:
        bg_image_info = background.load_bg_image_info(cfg)

    img_bg_map = background.get_img_bg_map(cfg, img_bg_list)


    img_shield_list = None
    if cfg.COMPOSITE.SHIELD.ENABLE:
        img_shield_list = shield.load_multiple_shield_imgs(cfg.COMPOSITE.SHIELD.ROOT)
    
    img_shield_v2_list = None
    shield_image_info = None    # cached image -> x,y,percentage info
    if cfg.COMPOSITE.SHIELD_V2.ENABLED:
        img_shield_v2_list = shield.load_shield_v2_imgs(cfg)
        if cfg.COMPOSITE.SHIELD_V2.FIX_RESOLUTION_PER_IMAGE.ENABLED:
            shield_image_info = shield.load_shield_image_info(cfg)
    img_shield_v2_map = shield.get_img_shield_map(cfg, img_shield_v2_list)

    # attribute_distribution
    attribute_distribution_list = attribute_manager.load_attribute_distribution_file(cfg)

    render_config.setup_basic_render(cfg)

    for mesh_id in tqdm(range(cfg.PROCESS.FIRST_INDEX, cfg.PROCESS.LAST_INDEX+1)):
        # resume
        if cfg.PROCESS.RESUME == True:
            render_results_exist = resume_utils.check_rendering_result_exist(cfg, mesh_id)
            if render_results_exist:
                print(f"Mesh {mesh_id} rendered, skip...")
                continue

        mesh_file_name = mesh_utils.format_mesh_file_name(mesh_id, cfg.SOURCE.OBJ_POSE_NAME, suffix="mhx2")
        obj_file_path = os.path.join(cfg.SOURCE.ROOT, mesh_file_name)

        # render_one_person(cfg, obj_file_path, img_bg_list, bg_image_info, img_shield_list, img_shield_v2_list, shield_image_info)
        render_one_person_v2(cfg, obj_file_path, img_bg_list, img_bg_map, bg_image_info, img_shield_list, img_shield_v2_list, img_shield_v2_map, shield_image_info, attribute_distribution_list)


def render_one_person_v2(cfg, obj_file_path, img_bg_list, img_bg_map, bg_image_info, img_shield_list, img_shield_v2_list, img_shield_v2_map, shield_image_info, attribute_distribution_list):

    # 1. load_obj
    obj_key, obj_person = load_person_obj(cfg, obj_file_path)

    # 2. generate render_params
    render_attribute_list = compose_render_params_list(cfg, obj_person, obj_file_path, img_bg_list, bg_image_info, img_shield_v2_list, shield_image_info)

    # 2-2. possible expand
    if cfg.EXPERIMENT.EXPAND.ENABLED:
        render_attribute_list = expand.expand_render_attribute_list(cfg, render_attribute_list)

    # 3. render & record_attribute
    for render_attribute in render_attribute_list:
        
        # if use the attribute sampled from the distribution
        if cfg.ATTRIBUTE.USE_DISTRIBUTION_FILE.RANDOM_SAMPLE.ENABLED:
            render_attribute = attribute_manager.attempt_override_attribute(render_attribute, attribute_distribution_list)

        render_one_person_by_render_params(obj_person, render_attribute, img_bg_map, img_shield_v2_map)
        if cfg.ATTRIBUTE.ENABLED:
            attribute_save_name = os.path.basename(render_attribute.save_path).replace(".jpg", ".json")
            attribute_save_path = attribute_manager.generate_attribute_save_path(cfg, render_attribute.mesh_id, render_attribute.camera_idx, render_attribute.seq_idx, save_name=attribute_save_name)
            attribute_manager.save_attribute_dict(cfg, attribute_save_path, render_attribute)

    # remove obj for next render
    bpy_utils.remove_object_v2(obj_key=obj_key)


def load_person_obj(cfg, obj_file_path):
    # TODO: add partner logic 

    # load and fetch obj for current person
    mesh_utils.load_object(obj_file_path)
    obj_key = mesh_utils.get_obj_key(obj_file_path)
    obj_person = bpy.data.objects[obj_key]
    # correct alpha for materials to avoid incorrect transparent
    bpy_utils.correct_alpha_channel()

    return obj_key, obj_person


def compose_render_params_list(cfg, 
    obj_person,
    obj_file_path,
    img_bg_list,
    bg_image_info,
    img_shield_v2_list,
    shield_image_info
    ):

    # select c_i cameras from `total_camera_count`, and fetch m images for each camera
    total_camera_count = cfg.PROCESS.TOTAL_CAMERA_COUNT
    camera_count_per_id = cfg.PROCESS.CAMERA_COUNT_PER_ID
    image_count_per_camera = cfg.PROCESS.IMAGE_COUNT_PER_CAMERA
    camera_ids = np.random.choice(range(total_camera_count), camera_count_per_id, replace=False)
    camera_ids.sort()
    seq_idx = 0

    render_attribute_list = []

    for camera_idx in camera_ids:
        pose_paths = pose_manager.fetch_pose_paths_in_one_camera(cfg, image_count_per_camera)
        for pose_path in pose_paths:
            # compose one image
            seq_idx += 1

            # camera: distance, elev, azim, cre_x_bia, ...
            camera_azim = camera_config.get_random_camera_azim(cfg)
            camera_elev = camera_config.get_random_camera_elev(cfg)
            camera_distance = camera_config.get_random_camera_distance(cfg, camera_elev, obj_person)
            cre_x_bias, cre_y_bias, cre_z_bias = camera_config.get_adjusted_camera_rotation(cfg, obj_person, camera_elev)

            # light
            light_azim = light_config.get_random_light_azim(cfg, camera_azim)
            light_elev = light_config.get_random_light_elev(cfg, camera_elev)
            light_distance = light_config.get_random_light_distance(cfg, camera_distance)

            # background
            # TODO: use a pure get method
            bg_name = background.random_get_one_bg_name(cfg, img_bg_list, camera_idx)
            # pose
            pose_name = os.path.basename(pose_path)

            # render_resolution
            if not cfg.BACKGROUND.FIX_RESOLUTION_PER_IMAGE.ENABLED:
                resolution_x, resolution_y, resolution_percentage = render_config.get_random_render_resolution(cfg)
            else:
                resolution_x, resolution_y, resolution_percentage = render_config.get_random_render_resolution_by_bg_image(cfg, bg_name, bg_image_info)
            img_width = int(resolution_x * resolution_percentage / 100)
            img_height = int(resolution_y * resolution_percentage / 100)

            # shield
            img_shield_v2_name = shield.random_select_one_shield_v2_name(cfg, img_shield_v2_list)
            if len(img_shield_v2_name) == 2 and cfg.COMPOSITE.SHIELD_V2.FIX_RESOLUTION_PER_IMAGE.ENABLED:
                resolution_x, resolution_y, resolution_percentage = render_config.get_random_render_resolution_by_bg_image(cfg, img_shield_v2_name[0], shield_image_info)
                img_width = int(resolution_x * resolution_percentage / 100)
                img_height = int(resolution_y * resolution_percentage / 100)

            # world_color
            world_color, world_color_to_background = world_config.get_world_background_color_by_camera_id(cfg, camera_idx)

            # gamma
            gamma_value = compositing.random_select_gamma_value(cfg, camera_idx)

            # meth_id
            mesh_id = mesh_utils.get_mesh_id(obj_file_path)


            # save_path
            save_path = render_config.generate_save_path(cfg, mesh_id, camera_idx, seq_idx)

            cur_attribute = Attribute(
                mesh_id, 
                camera_azim, 
                camera_elev, 
                camera_distance, 
                light_azim, 
                light_elev, 
                light_distance, 
                background=bg_name,
                pose=pose_name,
                camera_idx=camera_idx,
                img_width=img_width,
                img_height=img_height,
                partner_exist=False,    # TODO
                partner_mesh_id_list=[],    # TODO
                cre_x_bias=cre_x_bias,
                cre_y_bias=cre_y_bias,
                cre_z_bias=cre_z_bias,
                world_color=world_color,
                world_color_to_background=world_color_to_background,
                seq_idx=seq_idx,
                pose_path=pose_path,
                save_path=save_path,
                img_shield_v2_name=img_shield_v2_name,
                gamma_value=gamma_value
            )
            render_attribute_list.append(cur_attribute)
    
    return render_attribute_list

    
def render_one_person_by_render_params(obj_person, render_attribute, img_bg_map, img_shield_v2_map):

    camera = bpy.data.objects['Camera']
    render = bpy.data.scenes['Scene'].render
    light = bpy.data.objects['Light']

    # set pose
    bpy.ops.mcp.load_pose(filepath=render_attribute.pose_path)
    pose_manager.apply_transform_to_bones(obj_person)
    bpy.context.view_layer.update()

    # set camera
    person_location = (obj_person.location[0], obj_person.location[1], obj_person.location[2])
    camera_location = geometry.calculate_target_location(person_location, render_attribute.camera_distance, render_attribute.camera_azim, render_attribute.camera_elev)
    camera.location = camera_location
    bpy.context.view_layer.update()

    print(f"person_location: {person_location}")
    print(f"camera_location: {camera_location}")
    print(f"camera_rotation: {camera.rotation_euler}")
    camera_config.set_camera_roration(camera, obj_person, render_attribute.cre_x_bias, render_attribute.cre_y_bias, render_attribute.cre_z_bias)
    print(f"camera_rotation: {camera.rotation_euler}")
    
    # set light
    light.location = geometry.calculate_target_location(obj_person.location, render_attribute.light_distance, render_attribute.light_azim, render_attribute.light_elev)

    bpy.context.view_layer.update()

    # set background
    background.set_background_node_by_bg_name(img_bg_map, render_attribute.background)

    # set shield
    img_shield_v2_name = render_attribute.img_shield_v2_name
    shield.set_shield_v2_info_by_name(img_bg_map, img_shield_v2_map, img_shield_v2_name, render_attribute.img_width, render_attribute.img_height)

    # set world_color
    world_config.attemp_apply_world_color_v2(render_attribute.world_color, render_attribute.world_color_to_background)
    
    # set gamma
    compositing.set_gamma_value(render_attribute.gamma_value)

    # render
    render_config.modify_render_config_v2(render_attribute.img_width, render_attribute.img_height, 100)
    
    render.filepath = render_attribute.save_path
    bpy.ops.render.render(write_still=True)


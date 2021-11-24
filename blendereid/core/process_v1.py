
import os
import bpy
import random
from blendereid.core import background, compositing, camera_config, render_config, pose_manager, world_config, \
    attribute_manager
from blendereid.core import partner
from blendereid.utils import bpy_utils, mesh_utils, determinastic_utils, geometry
from blendereid.schema.attribute import Attribute


def render_one_person(cfg, obj_file_path, img_bg_list, bg_image_info, img_shield_list, img_shield_v2_list, shield_image_info, determinastic_params=None):

    partner_obj_key = None
    partner_obj_person = None
    if cfg.PARTNER.ENABLED:
        if random.random() < cfg.PARTNER.PROB:
            partner_obj_file_path = partner.random_select_one_partner(cfg)
            mesh_utils.load_object(partner_obj_file_path)
            partner_obj_key = mesh_utils.get_obj_key(partner_obj_file_path)
            partner_obj_person = bpy.data.objects[partner_obj_key]
            print(f"partner_obj_person's location: {partner_obj_person.location}")
            print(f"partner_obj_person's dimensions: {partner_obj_person.dimensions}")
            
    # load and fetch obj for current person
    mesh_utils.load_object(obj_file_path)
    obj_key = mesh_utils.get_obj_key(obj_file_path)
    obj_person = bpy.data.objects[obj_key]

    # correct alpha for materials to avoid incorrect transparent
    bpy_utils.correct_alpha_channel()


    # start to render
    # TODO: abstract this into a method
    distance_person_weight_factor = cfg.CAMERA.DISTANCE.PERSON_HEIGHT_FACTOR
    if cfg.CAMERA.OCCATIONAL_JUMP.ENABLE:
        if random.random() < cfg.CAMERA.OCCATIONAL_JUMP.PROB:
            distance_person_weight_factor = cfg.CAMERA.OCCATIONAL_JUMP.DISTANCE.PERSON_HEIGHT_FACTOR

    distance = (0.2 + cfg.CAMERA.DISTANCE.PERSON_HEIGHT_FACTOR * obj_person.dimensions[2]) + random.uniform(cfg.CAMERA.DISTANCE.RANDOM.LOWER_BOUND, cfg.CAMERA.DISTANCE.RANDOM.UPPER_BOUND) # for mhx2
    image_count_cur_id = cfg.PROCESS.IMAGE_COUNT_PER_ID + random.uniform(cfg.PROCESS.IMAGE_COUNT_PER_ID_RANDOM_LOWER_BOUND, cfg.PROCESS.IMAGE_COUNT_PER_ID_RANDOM_UPPER_BOUND)
    pose_count = int(image_count_cur_id / cfg.PROCESS.CONTINUOUS_COUNT)
    pose_names = pose_manager.fetch_pose_names(cfg, pose_count)
    pose_paths = [os.path.join(cfg.POSE.ROOT, f'{pose_name}') for pose_name in pose_names]

    idx_offset = 1
    for pose_idx, pose_path in enumerate(pose_paths):
        camera_parameters = []
        elev = camera_config.get_random_camera_elev(cfg)
        cur_distance = distance + float(elev - 10) * 0.12 * (1+(max(0, obj_person.dimensions[2] - 15) / 100))

        # [Determinstic Value] set camera_distance
        cur_distance = determinastic_utils.set_variable_according_to_determinastic_params(cur_distance, 'camera_distance', determinastic_params)

        # 3+3
        azim_rand = random.randint(0, 360)
        if cfg.CAMERA.AVERAGE_AZIM.ENABLED:
            azim_rand = int(pose_idx * (360 / len(pose_paths)))

        for continuous_idx in range(0, cfg.PROCESS.CONTINUOUS_COUNT):
            disturb = random.randint(-10, 10)
            azim = (azim_rand + disturb) % 360
            if cfg.DEBUG.ONE_IMAGE_PER_PERSON:
                azim = -60
            
            # [Determinstic Value] set camera_elev
            elev = determinastic_utils.set_variable_according_to_determinastic_params(elev, 'camera_elev', determinastic_params)
            # [Determinstic Value] set camera_elev
            azim = determinastic_utils.set_variable_according_to_determinastic_params(azim, 'camera_azim', determinastic_params)

            camera_parameters.append((cur_distance, elev, azim))
        # azim_rand = (azim_rand + 90) % 360
        # for disturb in [0, 10, 20]:
        #     azim = azim_rand + disturb % 360            
        #     camera_parameters.append((distance, elev, azim))
        idx_offset = render_one_person_one_pose(cfg, obj_file_path, obj_person, pose_path, camera_parameters, idx_offset=idx_offset, img_bg_list=img_bg_list, bg_image_info=bg_image_info, img_shield_list=img_shield_list, img_shield_v2_list=img_shield_v2_list, shield_image_info=shield_image_info, partner_obj_person=partner_obj_person)
        if cfg.DEBUG.ONE_IMAGE_PER_PERSON:
            break
    
    # remove obj for next render
    bpy_utils.remove_object_v2(obj_key=obj_key)
    bpy_utils.remove_object_v2(obj_key=partner_obj_key)


def render_one_person_one_pose(cfg, obj_file_path, obj_person, pose_path, camera_parameters, idx_offset=0, img_bg_list=[], bg_image_info=None, img_shield_list=[], img_shield_v2_list=[], shield_image_info=None, partner_obj_person=None):

    load_pos = os.path.splitext(os.path.basename(obj_file_path))[1] == '.mhx2'
    if load_pos:
        bpy.ops.mcp.load_pose(filepath=pose_path)
        pose_manager.apply_transform_to_bones(obj_person)
        bpy.context.view_layer.update()
    
    print(f"object_person's location: {obj_person.location}")
    print(f"object_person's dimensions: {obj_person.dimensions}")

    camera = bpy.data.objects['Camera']
    render = bpy.data.scenes['Scene'].render
    light = bpy.data.objects['Light']
    idx = idx_offset
    for (distance, elev, azim) in camera_parameters:
        # TODO: remove this: no use, here keep same with original code
        camera_index = random.randint(0, 5)
        # TODO: modify this: in fact, it is idx-1, here keep same with original code
        camera_idx = int((idx+1) / cfg.PROCESS.IMAGE_COUNT_PER_CAMERA)
        # prw_background.random_crop_background_from_prw(img_bg_list, camera_index)
        bg_name = background.random_select_one_background_img(cfg, img_bg_list, camera_idx)

        # print(f"distance:{distance}, elev: {elev}, azim: {azim}")

        person_location = (obj_person.location[0], obj_person.location[1], obj_person.location[2])
        camera.location = geometry.calculate_target_location(person_location, distance, azim, elev)

        if partner_obj_person is not None:
            if random.random() < cfg.PARTNER.PROB_IN_ONE_PERSON:
                partner.set_partner_location_and_rotation(cfg, person_location, partner_obj_person, azim)
            else:
                partner_obj_person.location = (9999, 9999, 9999)


        # print(light.location)
        # light.location = geometry.calculate_target_location(obj_person.location, distance/1.5, azim, 75)

        light_azim = (azim + random.randint(cfg.LIGHT.AZIM.RANDOM_LOWER_BOUND, cfg.LIGHT.AZIM.RANDOM_UPPER_BOUND)) % 360
        light_elev = cfg.LIGHT.ELEV.BASE
        light_distance = distance / 1.5
        light.location = geometry.calculate_target_location(obj_person.location, light_distance, light_azim, light_elev)
        # light.location = geometry.calculate_target_location(obj_person.location, distance/1.5, random.randint(0, 359), 75)

        bpy.context.view_layer.update()
        
        cre_x_bias, cre_y_bias, cre_z_bias = camera_config.adjust_camera_roration(camera, obj_person, cfg, elev, distance)
        
        mesh_id = mesh_utils.get_mesh_id(obj_file_path)
        render.filepath = render_config.generate_save_path(cfg, mesh_id, camera_idx, idx)

        if not cfg.BACKGROUND.FIX_RESOLUTION_PER_IMAGE.ENABLED:
            render_config.modify_render_config(cfg)
        else:
            render_config.modify_render_config_by_bg_image(cfg, os.path.basename(bg_name.filepath), bg_image_info)

        img_shield = compositing.random_select_one_shield(cfg, img_shield_list)
        img_shield_v2 = compositing.random_select_one_shield_v2(cfg, img_shield_v2_list)
        compositing.adjust_render_nodes(cfg, img_shield, img_shield_v2, shield_image_info)

        world_config.attemp_apply_world_color(cfg, camera_idx)
        bpy.ops.render.render(write_still=True)

        partner_exist = False if partner_obj_person is None else True
        partner_mesh_id_list = [] if partner_obj_person is None else [mesh_utils.get_mesh_id_from_obj_name(partner_obj_person.name)]
        
        # record attribute
        if cfg.ATTRIBUTE.ENABLED:
            img_percentage = render.resolution_percentage
            img_width = int(render.resolution_x * img_percentage / 100)
            img_height = int(render.resolution_y * img_percentage / 100)
            background_name = os.path.basename(bg_name.filepath) if bg_name is not None else ""
            attribute_obj = Attribute(
                mesh_id=mesh_id,
                camera_azim=azim,
                camera_elev=elev,
                camera_distance=distance,
                light_azim=light_azim,
                light_elev=light_elev,
                light_distance=light_distance,
                # TODO: verify basename is enough
                background=background_name,
                pose=os.path.basename(pose_path),
                camera_idx=camera_idx,
                img_width=img_width,
                img_height=img_height,
                partner_exist=partner_exist,
                partner_mesh_id_list=partner_mesh_id_list,
                cre_x_bias=cre_x_bias,
                cre_y_bias=cre_y_bias,
                cre_z_bias=cre_z_bias
            )
            attribute_save_path = attribute_manager.generate_attribute_save_path(cfg, mesh_id, camera_idx, idx)
            attribute_manager.save_attribute_dict(cfg, attribute_save_path, attribute_obj)

        idx += 1
        
        if cfg.DEBUG.ONE_IMAGE_PER_PERSON:
            break

        # I think this code is too dirty, but can not find alternative now
        if cfg.PROCESS.IMAGE_COUNT_PER_BACKGROUND > 1:
            for bgc in range(1, cfg.PROCESS.IMAGE_COUNT_PER_BACKGROUND):
                # vary pose
                if load_pos and cfg.PROCESS.POSE_CHANGE:
                    pose_path = pose_manager.find_adjacent_pose_path(pose_path)
                    bpy.ops.mcp.load_pose(filepath=pose_path)
                    pose_manager.apply_transform_to_bones(obj_person)
                    bpy.context.view_layer.update()


                # random camera
                distance = distance * random.uniform(0.80, 1.20)
                camera.location = geometry.calculate_target_location(person_location, distance, azim, elev)
                cre_x_bias, cre_y_bias, cre_z_bias = camera_config.adjust_camera_roration(camera, obj_person, cfg, elev, distance)
                # random resolution
                if not cfg.BACKGROUND.FIX_RESOLUTION_PER_IMAGE.ENABLED:
                    render_config.modify_render_config(cfg)
                else:
                    render_config.modify_render_config_by_bg_image(cfg, os.path.basename(bg_name.filepath), bg_image_info)
                compositing.adjust_render_nodes(cfg, img_shield, img_shield_v2, shield_image_info)
                # render
                render.filepath = render_config.generate_save_path(cfg, mesh_id, camera_idx, idx)
                bpy.ops.render.render(write_still=True)
                # record attribute
                if cfg.ATTRIBUTE.ENABLED:
                    img_percentage = render.resolution_percentage
                    img_width = int(render.resolution_x * img_percentage / 100)
                    img_height = int(render.resolution_y * img_percentage / 100)
                    background_name = os.path.basename(bg_name.filepath) if bg_name is not None else ""

                    attribute_obj = Attribute(
                        mesh_id=mesh_id,
                        camera_azim=azim,
                        camera_elev=elev,
                        camera_distance=distance,
                        light_azim=light_azim,
                        light_elev=light_elev,
                        light_distance=light_distance,
                        # TODO: verify basename is enough
                        background=background_name,
                        pose=os.path.basename(pose_path),
                        camera_idx=camera_idx,
                        img_width=img_width,
                        img_height=img_height,
                        partner_exist=partner_exist,
                        partner_mesh_id_list=partner_mesh_id_list,
                        cre_x_bias=cre_x_bias,
                        cre_y_bias=cre_y_bias,
                        cre_z_bias=cre_z_bias
                    )
                    attribute_save_path = attribute_manager.generate_attribute_save_path(cfg, mesh_id, camera_idx, idx)
                    attribute_manager.save_attribute_dict(cfg, attribute_save_path, attribute_obj)
                idx +=1

    return idx

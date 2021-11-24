import bpy
import random


# world color relative
DEFAULT_WORLD_BACKGROUND_COLOR = (0.05087608844041824, 0.05087608844041824, 0.05087608844041824, 1.0)   # no use current
DEFAULT_WORLD_BACKGROUND_COLOR_V2 = (0.0509, 0.0509, 0.0509, 1.0)   # no use current
DEFAULT_COLOR_MASK = (0.0, 0.0, 0.0, 0.0)

def get_original_world_background_color():
    color = bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value
    return color

def apply_world_background_color(cfg, color=(0.3, 0.1, 0.8, 0.5)):
    # light material effect
    apply_world_color_frontend(color)
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.APPLY_TO_BACKGROUND:
        apply_color_mask_alpha(color)

def apply_world_color_frontend(color):
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = color

def apply_color_mask_alpha(color_mask=(0.0, 0.0, 0.0, 0.0)):
    color_mask_alpha_node = bpy.context.scene.node_tree.nodes.get("Alpha Over.002")
    color_mask_alpha_node.inputs[0].default_value = color_mask[3]
    color_mask_node = bpy.context.scene.node_tree.nodes.get("RGB")
    color_mask_node.outputs[0].default_value = color_mask

def reset_to_original_world(cfg):
    apply_world_background_color(cfg, DEFAULT_WORLD_BACKGROUND_COLOR)
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.APPLY_TO_BACKGROUND:
        apply_color_mask_alpha(DEFAULT_COLOR_MASK)

def set_world_background_color_by_camera_id(cfg, camera_id):
    camera_world_color_map = {
        1: (0.85, 0.85, 0.05, 0.2),
        2: (0.85, 0.05, 0.05, 0.2),
        3: (0.05, 0.05, 0.85, 0.2),
        # 4: (0.05, 0.85, 0.85, 0.2),
        # 5: (0.85, 0.05, 0.85, 0.2),
        # 6: (0.85, 0.85, 0.85, 0.2),
    }

    
    world_color_scale = 1.0
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.ENABLED:
        world_color_scale = random.uniform(cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.LOWER_BOUND, cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.UPPER_BOUND)

    world_color_values = cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.VALUES
    for (i, value) in enumerate(world_color_values):
        s1, s2, s3 = fetch_wc_random_scales(cfg, world_color_scale)
        value_random = [value[0] * s1, value[1] * s2, value[2] * s3, value[3]]
        camera_world_color_map[i+1] = value_random
    
    if camera_id in camera_world_color_map:
        color = camera_world_color_map[camera_id]
        apply_world_background_color(cfg, color)
    else:
        reset_to_original_world(cfg)

def attemp_apply_world_color(cfg, camera_idx):
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.ENABLE:
        set_world_background_color_by_camera_id(cfg, camera_idx)


def fetch_wc_random_scales(cfg, world_color_scale):
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.INDEPENDENT:
        s1 = random.uniform(cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.LOWER_BOUND, cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.UPPER_BOUND)
        s2 = random.uniform(cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.LOWER_BOUND, cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.UPPER_BOUND)
        s3 = random.uniform(cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.LOWER_BOUND, cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.UPPER_BOUND)
    else:
        s1 = world_color_scale
        s2 = world_color_scale
        s3 = world_color_scale
    return s1, s2, s3


def get_world_background_color_by_camera_id(cfg, camera_id):
    if not cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.ENABLE:
        return DEFAULT_WORLD_BACKGROUND_COLOR, DEFAULT_COLOR_MASK


    camera_world_color_map = {
        1: (0.85, 0.85, 0.05, 0.2),
        2: (0.85, 0.05, 0.05, 0.2),
        3: (0.05, 0.05, 0.85, 0.2),
        # 4: (0.05, 0.85, 0.85, 0.2),
        # 5: (0.85, 0.05, 0.85, 0.2),
        # 6: (0.85, 0.85, 0.85, 0.2),
    }
    world_color_scale = 1.0
    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.ENABLED:
        world_color_scale = random.uniform(cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.LOWER_BOUND, cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.RANDOM.UPPER_BOUND)

    world_color_values = cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.VALUES
    for (i, value) in enumerate(world_color_values):
        s1, s2, s3 = fetch_wc_random_scales(cfg, world_color_scale)
        value_random = [value[0] * s1, value[1] * s2, value[2] * s3, value[3]]
        camera_world_color_map[i+1] = value_random
    
    color = camera_world_color_map[camera_id] if camera_id  in camera_world_color_map else DEFAULT_WORLD_BACKGROUND_COLOR_V2
    color_to_background = color if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.APPLY_TO_BACKGROUND else DEFAULT_COLOR_MASK

    if cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.BACKGROUND.ENABLED:
        world_color_background_values = cfg.OPTION.APPLY_CAMERA_WORLD_COLOR.BACKGROUND.VALUES
        camera_world_background_color_map = {}
        for (i, value) in enumerate(world_color_background_values):
            s1, s2, s3 = 1.0, 1.0, 1.0
            value_random = [value[0] * s1, value[1] * s2, value[2] * s3, value[3]]
            camera_world_background_color_map[i+1] = value_random
            color_to_background = camera_world_background_color_map[camera_id] if camera_id  in camera_world_background_color_map else DEFAULT_COLOR_MASK

    return color, color_to_background

def attemp_apply_world_color_v2(color, color_to_background):
    apply_world_color_frontend(color)
    apply_color_mask_alpha(color_to_background)
import os
import bpy
import random
import numpy as np
from blendereid.core import background, render_config

def compose_render_nodes(default_bg_file_path=None):
    # TODO: remove this code
    if default_bg_file_path is None:
        default_bg_file_path = 'data_demo/background_demo/bg_blender_notext.png'
    # add background
    bg_file_path = os.path.abspath(default_bg_file_path)
    img_bg = bpy.data.images.load(bg_file_path)

    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    composite_node = tree.nodes.get("Composite")
    render_node = tree.nodes.get("Render Layers")

    image_node = tree.nodes.new("CompositorNodeImage")
    image_node.image = img_bg
    scale_node = tree.nodes.new("CompositorNodeScale")
    alpha_node = tree.nodes.new("CompositorNodeAlphaOver")
    scale_node.space = 'RELATIVE'
    scale_node.space = 'RENDER_SIZE'

    
    gamma_node = tree.nodes.new("CompositorNodeGamma")

    # crop_node = tree.nodes.new("CompositorNodeCrop")
    # crop_node.relative = False
    # crop_node.use_crop_size = True
    # crop_node.min_x = 0
    # crop_node.min_y = 0
    # crop_node.max_x = 128
    # crop_node.max_y = 256


    # Image.001
    shield_image_node = tree.nodes.new("CompositorNodeImage")
    shield_scale_node = tree.nodes.new("CompositorNodeScale")
    shield_scale_node.space = 'ABSOLUTE'
    shield_transform_node = tree.nodes.new("CompositorNodeTransform")
    # Alpha Over.001
    shield_alpha_node = tree.nodes.new("CompositorNodeAlphaOver")

    # add for color mask
    # Alpha Over.002
    color_mask_alpha_node = tree.nodes.new("CompositorNodeAlphaOver")
    color_mask_alpha_node.inputs[0].default_value = 0.0
    color_mask_node = tree.nodes.new("CompositorNodeRGB")
    color_mask_node.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0)


    links = tree.links
    # link = links.new(image_node.outputs[0], crop_node.inputs[0])
    # link = links.new(crop_node.outputs[0], scale_node.inputs[0])
    link = links.new(image_node.outputs[0], scale_node.inputs[0])
    # link = links.new(scale_node.outputs[0], alpha_node.inputs[1])
    link = links.new(scale_node.outputs[0], color_mask_alpha_node.inputs[1])
    link = links.new(color_mask_node.outputs[0], color_mask_alpha_node.inputs[2])

    # color_mask_alpha_node + render_node -> alpha_node
    link = links.new(color_mask_alpha_node.outputs[0], alpha_node.inputs[1])
    link = links.new(render_node.outputs[0], alpha_node.inputs[2])

    # shelter branch
    link = links.new(shield_image_node.outputs[0], shield_scale_node.inputs[0])
    link = links.new(shield_scale_node.outputs[0], shield_transform_node.inputs[0])
    link = links.new(shield_transform_node.outputs[0], shield_alpha_node.inputs[2])
    link = links.new(alpha_node.outputs[0], shield_alpha_node.inputs[1])

    
    link = links.new(shield_alpha_node.outputs[0], gamma_node.inputs[0])
    link = links.new(gamma_node.outputs[0], composite_node.inputs[0])


def adjust_render_nodes(cfg, img_shield, img_shield_v2=None, shield_image_info=None):

    # for gamma
    if cfg.COMPOSITE.GAMMA.RANDOM.ENABLE:
        gamma_node = bpy.context.scene.node_tree.nodes.get("Gamma")
        gamma_node.inputs[1].default_value = cfg.COMPOSITE.GAMMA.RANDOM.BASE
        gamma_node.inputs[1].default_value += random.uniform(cfg.COMPOSITE.GAMMA.RANDOM.LOWER_BOUND, cfg.COMPOSITE.GAMMA.RANDOM.UPPER_BOUND)

    # for front front shield
    shield_image_node = bpy.context.scene.node_tree.nodes.get("Image.001")
    if cfg.COMPOSITE.SHIELD.ENABLE and img_shield is not None:
        # TODO: replace this image with new
        shield_image_node.image = img_shield
        
        # set the shield image size
        shield_scale_node = bpy.context.scene.node_tree.nodes.get("Scale.001")
        render = bpy.data.scenes['Scene'].render
        render_width = render.resolution_x
        render_height = render.resolution_y
        resolution_percentage = render.resolution_percentage
        shield_scale_node.space = 'ABSOLUTE'
        shield_scale_node.inputs[1].default_value = render_width * cfg.COMPOSITE.SHIELD.SCALE.WIDTH_SCALE.BASE * random.uniform(cfg.COMPOSITE.SHIELD.SCALE.WIDTH_SCALE.RANDOM.LOWER_BOUND, cfg.COMPOSITE.SHIELD.SCALE.WIDTH_SCALE.RANDOM.UPPER_BOUND) # X
        shield_scale_node.inputs[2].default_value = render_height * cfg.COMPOSITE.SHIELD.SCALE.HEIGHT_SCALE.BASE * random.uniform(cfg.COMPOSITE.SHIELD.SCALE.HEIGHT_SCALE.RANDOM.LOWER_BOUND, cfg.COMPOSITE.SHIELD.SCALE.HEIGHT_SCALE.RANDOM.UPPER_BOUND) # Y

        # set the shield image position
        shield_transform_node = bpy.context.scene.node_tree.nodes.get("Transform")
        shield_transform_node.inputs[1].default_value = render_width * cfg.COMPOSITE.SHIELD.TRANSFORM.X_SCALE.BASE * random.uniform(cfg.COMPOSITE.SHIELD.TRANSFORM.X_SCALE.RANDOM.LOWER_BOUND, cfg.COMPOSITE.SHIELD.TRANSFORM.X_SCALE.RANDOM.UPPER_BOUND) # X
        shield_transform_node.inputs[2].default_value = render_height * cfg.COMPOSITE.SHIELD.TRANSFORM.Y_SCALE.BASE * random.uniform(cfg.COMPOSITE.SHIELD.TRANSFORM.Y_SCALE.RANDOM.LOWER_BOUND, cfg.COMPOSITE.SHIELD.TRANSFORM.Y_SCALE.RANDOM.UPPER_BOUND) # Y

        print(f"render_width={render_width}, render_height={render_height}, percentage={resolution_percentage}")
        print(f"width={shield_scale_node.inputs[1].default_value}, height={shield_scale_node.inputs[2].default_value}")
        print(f"x={shield_transform_node.inputs[1].default_value}, y={shield_transform_node.inputs[2].default_value}")
    else:
        shield_image_node.image = None

    if cfg.COMPOSITE.SHIELD_V2.ENABLED and img_shield_v2 is not None:
        print(f"set shield_v2 node")
        (img_bg, img_fg) = img_shield_v2
        set_shield_img(img_fg)
        background.set_backgound_from_predefined_img(img_bg)
        # reset image resolution
        render_config.modify_render_config_by_bg_image(cfg, os.path.basename(img_bg.filepath), shield_image_info)


def set_shield_img(img_fg_shield):
    shield_image_node = bpy.context.scene.node_tree.nodes.get("Image.001")
    shield_image_node.image = img_fg_shield

    # set the shield image size
    shield_scale_node = bpy.context.scene.node_tree.nodes.get("Scale.001")
    render = bpy.data.scenes['Scene'].render
    render_width = render.resolution_x
    render_height = render.resolution_y
    resolution_percentage = render.resolution_percentage
    shield_scale_node.space = 'ABSOLUTE'
    shield_scale_node.inputs[1].default_value = render_width
    shield_scale_node.inputs[2].default_value = render_height

    # set the shield image position
    shield_transform_node = bpy.context.scene.node_tree.nodes.get("Transform")
    shield_transform_node.inputs[1].default_value = 0
    shield_transform_node.inputs[2].default_value = 0


def random_select_one_shield(cfg, img_shield_list):
    img_shield = None
    if cfg.COMPOSITE.SHIELD.ENABLE and random.random() < cfg.COMPOSITE.SHIELD.PROB:
        img_shield = np.random.choice(img_shield_list)
    return img_shield

# @deprecated, see `random_select_one_shield_v2` in shield.py
def random_select_one_shield_v2(cfg, img_shield_v2_list):
    img_shield_v2 = None
    if cfg.COMPOSITE.SHIELD_V2.ENABLED and random.random() < cfg.COMPOSITE.SHIELD_V2.PROB:
        num_shield_v2 = len(img_shield_v2_list)
        select_idx = np.random.choice(range(num_shield_v2))
        img_shield_v2 = img_shield_v2_list[select_idx]
    return img_shield_v2


def random_select_gamma_value(cfg, camera_id):
    # for gamma
    if cfg.COMPOSITE.GAMMA.RANDOM.ENABLE:
        if cfg.COMPOSITE.GAMMA.RANDOM.CAMERA_BASE:
            DEFAULT_GAMMA_VALUE = 1.0
            gamma_camera_map = {}
            for (i, value) in enumerate(cfg.COMPOSITE.GAMMA.RANDOM.CAMERA_VALUES):
                gamma_camera_map[i+1] = cfg.COMPOSITE.GAMMA.RANDOM.CAMERA_VALUES[i]
            gamma_value = gamma_camera_map[camera_id] if camera_id in gamma_camera_map else DEFAULT_GAMMA_VALUE
        else:
            gamma_value = cfg.COMPOSITE.GAMMA.RANDOM.BASE
            gamma_value += random.uniform(cfg.COMPOSITE.GAMMA.RANDOM.LOWER_BOUND, cfg.COMPOSITE.GAMMA.RANDOM.UPPER_BOUND)
        return gamma_value
    return 1.0

def set_gamma_value(gamma_value):
    if gamma_value is not None:
        gamma_node = bpy.context.scene.node_tree.nodes.get("Gamma")
        gamma_node.inputs[1].default_value = gamma_value


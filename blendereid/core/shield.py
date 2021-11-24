import os
import cv2
from tqdm import tqdm
import bpy
import json
import random
import numpy as np

from blendereid.core import background


def load_multiple_shield_imgs(shield_root):
    print(f"start to load images from {shield_root}")
    shield_img_list = []
    shield_names = os.listdir(shield_root)
    shield_names = sorted(shield_names)
    for shield_name in tqdm(shield_names):
        shield_file_path = os.path.join(shield_root, shield_name)
        shield_file_path = os.path.abspath(shield_file_path)
        img = cv2.imread(shield_file_path)
        img_bg = bpy.data.images.load(shield_file_path)
        shield_img_list.append(img_bg)
    print(f"total collect {len(shield_names)}, valid {len(shield_img_list)}...")
    return shield_img_list

def load_shield_v2_imgs(cfg):
    shiled_v2_root = cfg.COMPOSITE.SHIELD_V2.ROOT
    
    print(f"start to load images from {shiled_v2_root}")
    shield_v2_img_list = []
    shield_names = os.listdir(shiled_v2_root)
    shield_bg_names = list(filter(lambda x: x.find('_bg.png') > -1, shield_names))
    shield_bg_names = sorted(shield_bg_names)
    num_limit = cfg.COMPOSITE.SHIELD_V2.NUM_LIMIT
    if num_limit > 0:
        shield_bg_names = shield_bg_names[:num_limit]

    for shield_bg_name in tqdm(shield_bg_names):
        # bg
        shield_bg_file_path = os.path.join(shiled_v2_root, shield_bg_name)
        shield_bg_file_path = os.path.abspath(shield_bg_file_path)
        # img = cv2.imread(shield_file_path)
        img_bg = bpy.data.images.load(shield_bg_file_path)
        # fg
        shield_fg_name = shield_bg_name.replace("_bg.png", "_fg.png")
        shield_fg_file_path = os.path.join(shiled_v2_root, shield_fg_name)
        shield_fg_file_path = os.path.abspath(shield_fg_file_path)
        # img = cv2.imread(shield_file_path)
        img_fg = bpy.data.images.load(shield_fg_file_path)
        shield_v2_img_list.append((img_bg, img_fg))

    print(f"total collect {len(shield_bg_names)}, valid {len(shield_v2_img_list)}...")
    return shield_v2_img_list


def load_shield_image_info(cfg):
    """
    load cached shield_image_info, include x,y,p for each image
    """
    save_json_path = cfg.COMPOSITE.SHIELD_V2.FIX_RESOLUTION_PER_IMAGE.SAVE_JSON_PATH
    if not os.path.exists(save_json_path):
        raise ValueError(f'save_json_path not exist: {save_json_path}')
    
    print(f"Background Image Info cache is enabled, loading it from {save_json_path}")
    with open(save_json_path) as f:
        shield_image_info = json.load(f)
    return shield_image_info

def get_img_shield_map(cfg, img_shield_v2_list):
    """
    assume all image name is unique
    """
    img_shield_v2_map = {}
    if img_shield_v2_list is None:
        return img_shield_v2_map
    for img_shield_2 in img_shield_v2_list:
        for fg_or_bg in img_shield_2:
            img_shield_name = os.path.basename(fg_or_bg.filepath)
            img_shield_v2_map[img_shield_name] = fg_or_bg
    return img_shield_v2_map

def random_select_one_shield_v2_name(cfg, img_shield_v2_list):
    img_shield_v2 = None
    if cfg.COMPOSITE.SHIELD_V2.ENABLED and random.random() < cfg.COMPOSITE.SHIELD_V2.PROB:
        num_shield_v2 = len(img_shield_v2_list)
        select_idx = np.random.choice(range(num_shield_v2))
        img_shield_v2 = img_shield_v2_list[select_idx]
    
    if img_shield_v2 is not None:
        img_shield_v2_name = [os.path.basename(fg_or_bg.filepath) for fg_or_bg in img_shield_v2]
    else:
        img_shield_v2_name = []
    return img_shield_v2_name


def set_shield_v2_info_by_name(image_bg_map, image_shield_v2_map, image_shield_v2_name, resolution_x, resolution_y):
    shield_image_node = bpy.context.scene.node_tree.nodes.get("Image.001")
    shield_image_node.image = None

    if len(image_shield_v2_name) == 0:
        return
    (img_bg_name, img_fg_name) = image_shield_v2_name
    set_shield_v2_node_by_name(image_shield_v2_map, img_fg_name, resolution_x, resolution_y)
    background.set_background_node_by_bg_name(image_shield_v2_map, img_bg_name)


def set_shield_v2_node_by_name(image_shield_v2_map, image_fg_name, resolution_x, resolution_y):
    
    if image_fg_name is None or image_fg_name not in image_shield_v2_map:
        img_shield_v2_node = None
    else:
        img_shield_v2_node = image_shield_v2_map[image_fg_name]

    
    shield_image_node = bpy.context.scene.node_tree.nodes.get("Image.001")
    shield_image_node.image = img_shield_v2_node

    # set the shield image size
    shield_scale_node = bpy.context.scene.node_tree.nodes.get("Scale.001")
    render = bpy.data.scenes['Scene'].render
    render_width = resolution_x
    render_height = resolution_y
    resolution_percentage = 100
    shield_scale_node.space = 'ABSOLUTE'
    shield_scale_node.inputs[1].default_value = render_width
    shield_scale_node.inputs[2].default_value = render_height

    # set the shield image position
    shield_transform_node = bpy.context.scene.node_tree.nodes.get("Transform")
    shield_transform_node.inputs[1].default_value = 0
    shield_transform_node.inputs[2].default_value = 0

def set_shield_from_predefined_img(image_bg, image_fg, resolution_x, resolution_y):
    shield_image_node = bpy.context.scene.node_tree.nodes.get("Image.001")
    shield_image_node.image = image_fg

    # set the shield image size
    shield_scale_node = bpy.context.scene.node_tree.nodes.get("Scale.001")
    render = bpy.data.scenes['Scene'].render
    render_width = resolution_x
    render_height = resolution_y
    resolution_percentage = 100
    shield_scale_node.space = 'ABSOLUTE'
    shield_scale_node.inputs[1].default_value = render_width
    shield_scale_node.inputs[2].default_value = render_height

    # set the shield image position
    shield_transform_node = bpy.context.scene.node_tree.nodes.get("Transform")
    shield_transform_node.inputs[1].default_value = 0
    shield_transform_node.inputs[2].default_value = 0

    background.set_backgound_from_predefined_img(image_bg)

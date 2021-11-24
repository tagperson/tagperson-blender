import cv2
import os
import json
from tqdm import tqdm
import bpy
import random

def load_multiple_bg_imgs(cfg):
    if cfg.BACKGROUND.USE_EMPTY_BACKGROUND:
        return []
    bg_root = cfg.BACKGROUND.ROOT
    print(f"start to load images from {bg_root}")
    bg_img_list = []
    bg_names = os.listdir(bg_root)
    bg_names = sorted(bg_names)
    bg_names = list(filter(lambda x: x.find(".jpg") > -1, bg_names))
    num_limit = cfg.BACKGROUND.NUM_LIMIT
    if num_limit > 0:
        bg_names = bg_names[:num_limit]

    for bg_name in tqdm(bg_names):
        bg_file_path = os.path.join(bg_root, bg_name)
        bg_file_path = os.path.abspath(bg_file_path)
        img = cv2.imread(bg_file_path)
        h, w = img.shape[0], img.shape[1]
        if h / w > 5:
            continue
        img_bg = bpy.data.images.load(bg_file_path)
        bg_img_list.append(img_bg)
    print(f"total collect {len(bg_names)}, valid {len(bg_img_list)}...")
    return bg_img_list


def load_multiple_bg_imgs_group_by_camera(cfg):
    """
    This methods is parallel with `load_multiple_bg_imgs`
    return a dict where the key is `cid`, the value is list of background image node
    """
    bg_root = cfg.BACKGROUND.ROOT
    print(f"start to load images from {bg_root}")

    bg_imgs_dict = {}
    camera_ids = os.listdir(bg_root)
    for camera_id in camera_ids:
        camera_path = os.path.join(bg_root, camera_id)
        if not os.path.isdir(camera_path):
            raise ValueError(f"camera_path is not a dir {camera_path}")
        c_bg_names = os.listdir(camera_path)
        c_bg_names = list(filter(lambda x: x.find(".jpg") > -1, c_bg_names))
        c_bg_names = sorted(c_bg_names)
        num_limit = cfg.BACKGROUND.NUM_LIMIT
        if num_limit > 0:
            c_bg_names = c_bg_names[:num_limit]

        c_bg_img_list = []
        for bg_name in tqdm(c_bg_names):
            bg_file_path = os.path.join(camera_path, bg_name)
            bg_file_path = os.path.abspath(bg_file_path)
            img = cv2.imread(bg_file_path)
            h, w = img.shape[0], img.shape[1]
            if h / w > 5:
                continue
            img_bg = bpy.data.images.load(bg_file_path)
            c_bg_img_list.append(img_bg)
        bg_imgs_dict[int(camera_id)] =  c_bg_img_list
    return bg_imgs_dict
    



def random_select_one_background_img(cfg, img_bg_list, camera_index):
    if cfg.BACKGROUND.USE_CAMERA_GROUP:
        assert isinstance(img_bg_list, dict), f"cfg.BACKGROUND.USE_CAMERA_GROUP is enabled but `img_bg_list` is not a dict."
        num_camera = len(img_bg_list.keys())
        idx = camera_index % num_camera
        selected_img_bg_list = img_bg_list[idx]
    else:
        selected_img_bg_list = img_bg_list

    # set image content
    if img_bg_list is None or len(img_bg_list) == 0:
        img_bg = None
    else:
        img_bg = random.choice(selected_img_bg_list)

    img_bg = set_backgound_from_predefined_img(img_bg)
    # set scale
    return img_bg

def set_backgound_from_predefined_img(img_bg):
    image_node = bpy.context.scene.node_tree.nodes.get("Image")
    image_node.image = img_bg
    return img_bg


def load_bg_image_info(cfg):
    """
    load cached bg_image_info, include x,y,p for each image
    """
    save_json_path = cfg.BACKGROUND.FIX_RESOLUTION_PER_IMAGE.SAVE_JSON_PATH
    if not os.path.exists(save_json_path):
        raise ValueError(f'save_json_path not exist: {save_json_path}')
    
    print(f"Background Image Info cache is enabled, loading it from {save_json_path}")
    with open(save_json_path) as f:
        bg_image_info = json.load(f)
    return bg_image_info


def random_get_one_bg_name(cfg, img_bg_list, camere_idx):
    if cfg.BACKGROUND.USE_CAMERA_GROUP:
        assert isinstance(img_bg_list, dict), f"cfg.BACKGROUND.USE_CAMERA_GROUP is enabled but `img_bg_list` is not a dict."
        num_camera = len(img_bg_list.keys())
        idx = camere_idx % num_camera
        selected_img_bg_list = img_bg_list[idx]
    else:
        selected_img_bg_list = img_bg_list

    # set image content
    if img_bg_list is None or len(img_bg_list) == 0:
        img_bg = None
    else:
        img_bg = random.choice(selected_img_bg_list)

    bg_name = os.path.basename(img_bg.filepath) if img_bg is not None else None
    return bg_name


def get_img_bg_map(cfg, img_bg_list):
    """
    assume all image name is unique
    """
    img_bg_map = {}
    if cfg.BACKGROUND.USE_CAMERA_GROUP:
        assert isinstance(img_bg_list, dict), f"cfg.BACKGROUND.USE_CAMERA_GROUP is enabled but `img_bg_list` is not a dict."
        for key, c_img_bg_list in img_bg_list.items():
            for img_bg in c_img_bg_list:
                bg_name = os.path.basename(img_bg.filepath)
                img_bg_map[bg_name] = img_bg
    else:
        for img_bg in img_bg_list:
            bg_name = os.path.basename(img_bg.filepath)
            img_bg_map[bg_name] = img_bg
            
    return img_bg_map


def set_background_node_by_bg_name(img_bg_map, bg_name):

    if bg_name is None or bg_name not in img_bg_map:
        bg_node = None
    else:
        bg_node = img_bg_map[bg_name]    

    set_backgound_from_predefined_img(bg_node)


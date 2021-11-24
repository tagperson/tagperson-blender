"""
kind of augmentation, expand in certain factor
"""

import copy
import numpy as np
import random
import os

def expand_render_attribute_list(cfg, render_attribute_list):
    expanded_list = []
    base_num = len(render_attribute_list)
    for render_attribute in render_attribute_list:
        expanded_list.append(render_attribute)
        if cfg.EXPERIMENT.EXPAND.CAMERA_DISTANCE.ENABLED:
            for i in range(0, cfg.EXPERIMENT.EXPAND.CAMERA_DISTANCE.EXPAND_NUM):
                random_max = cfg.EXPERIMENT.EXPAND.CAMERA_DISTANCE.RANDOM.UPPER_BOUND
                random_min = cfg.EXPERIMENT.EXPAND.CAMERA_DISTANCE.RANDOM.LOWER_BOUND
                expand_render_attribute = expand_camera_distance(render_attribute, increment=base_num*(i+1), random_max=random_max, random_min=random_min)
                expanded_list.append(expand_render_attribute)
        if cfg.EXPERIMENT.EXPAND.CAMERA_ELEV.ENABLED:
            for i in range(0, cfg.EXPERIMENT.EXPAND.CAMERA_ELEV.EXPAND_NUM):
                random_max = cfg.EXPERIMENT.EXPAND.CAMERA_ELEV.RANDOM.UPPER_BOUND
                random_min = cfg.EXPERIMENT.EXPAND.CAMERA_ELEV.RANDOM.LOWER_BOUND
                expand_render_attribute = expand_camera_elev(render_attribute, increment=base_num*(cfg.EXPERIMENT.EXPAND.CAMERA_DISTANCE.EXPAND_NUM+i+1), random_max=random_max, random_min=random_min)
                expanded_list.append(expand_render_attribute)
        if cfg.EXPERIMENT.EXPAND.GAMMA.ENABLED:
            for i in range(0, cfg.EXPERIMENT.EXPAND.GAMMA.EXPAND_NUM):
                expand_render_attribute = expand_gamma_value(render_attribute, increment=base_num*(i+1))
                expanded_list.append(expand_render_attribute)

    return expanded_list


def add_increment_in_save_path(save_path: str, increment: int):
    save_root = os.path.dirname(save_path)
    save_path = os.path.basename(save_path)
    save_name, save_ext = os.path.splitext(save_path)
    info_array = save_name.split("_")
    seq_id = int(info_array[2]) + increment
    save_path = f"{info_array[0]}_{info_array[1]}_{seq_id}{save_ext}"
    save_path = os.path.join(save_root, save_path)
    return save_path

def expand_camera_distance(render_attribute, increment: int, random_max = 10, random_min = -10):
    expand_render_attribute = copy.deepcopy(render_attribute)
    expand_render_attribute.camera_distance += random.uniform(random_min, random_max)
    expand_render_attribute.save_path = add_increment_in_save_path(expand_render_attribute.save_path, increment)
    return expand_render_attribute

def expand_camera_elev(render_attribute, increment: int, random_max = 10, random_min = -10):
    expand_render_attribute = copy.deepcopy(render_attribute)
    expand_render_attribute.camera_elev += random.uniform(random_min, random_max)
    expand_render_attribute.camera_elev = max(0, expand_render_attribute.camera_elev)
    expand_render_attribute.save_path = add_increment_in_save_path(expand_render_attribute.save_path, increment)
    return expand_render_attribute

def expand_gamma_value(render_attribute, increment: int):
    expand_render_attribute = copy.deepcopy(render_attribute)
    expand_render_attribute.gamma_value = round(random.uniform(0.2, 2.5), 3)
    expand_render_attribute.save_path = add_increment_in_save_path(expand_render_attribute.save_path, increment)
    return expand_render_attribute
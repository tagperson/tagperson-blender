import os
import json
import numpy as np

def generate_attribute_save_path(cfg, mesh_id, camera_index, sequence_id, save_name=None):
    if cfg.OUTPUT_DIR_FOR_ATTRIBUTE != '':
        output_dir = cfg.OUTPUT_DIR_FOR_ATTRIBUTE
    else:
        output_dir = os.path.join(cfg.OUTPUT_DIR, "output_attributes")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if save_name is None:
        save_name = f"{mesh_id}_c{camera_index}s1_{int(sequence_id)}.json"
    save_path = f"{output_dir}/{save_name}"
    return save_path


def save_attribute_dict(cfg, save_path, attribute):
    attribute_dict = attribute.__dict__

    non_save_key_list = [
        'pose_path',
        'save_path',
    ]
    for non_save_key in non_save_key_list:
        if non_save_key in attribute_dict:
            del attribute_dict[non_save_key]
    
    print(attribute_dict)

    with open(save_path, 'w') as f:
        json.dump(attribute_dict, f)


def override_attribute_with_given_dict(render_attribute, render_options_dict):
    if render_options_dict is None:
        return render_attribute
    for key, value in render_options_dict.items():
        
        # TODO: temp logic in 20210909
        if key == 'img_height':
            continue
        if key == 'img_width':
            assert 'img_height' in render_options_dict
            target_ratio = render_options_dict['img_height'] / render_options_dict['img_width']
            target_width = render_attribute.img_width
            target_height = int(target_width * target_ratio)
            setattr(render_attribute, 'img_height', target_height)
            continue
        # temp light_azim_rela in 20210925
        if key == 'light_azim':
            assert hasattr(render_attribute, 'camera_azim') == True
            target_light_azim = (render_attribute.camera_azim + render_options_dict['light_azim']) % 360
            setattr(render_attribute, "light_azim", target_light_azim)

        setattr(render_attribute, key, value)
    return render_attribute


def load_attribute_distribution_file(cfg):
    """
    the file is json format.
    the content in the file is a list, where each element is a serial of attribute
    """
    if not cfg.ATTRIBUTE.USE_DISTRIBUTION_FILE.ENABLED:
        return None
    
    distribute_file_path = cfg.ATTRIBUTE.USE_DISTRIBUTION_FILE.FILE_PATH
    if not os.path.exists(distribute_file_path):
        raise ValueError(f'attribute use distribute file is enabled, but the file {distribute_file_path} not exist')

    with open(distribute_file_path) as f:
        attribute_distribute_list = json.load(f)
    
    attribute_distribute_list = filter_attribute_distribution_list_by_limit_fields(cfg, attribute_distribute_list)
    return attribute_distribute_list


def filter_attribute_distribution_list_by_limit_fields(cfg, attribute_distribution_list):
    limit_fields = cfg.ATTRIBUTE.USE_DISTRIBUTION_FILE.LIMIT_FIELDS
    if len(limit_fields) == 0:
        return attribute_distribution_list
    
    limit_fields_dict = set(limit_fields)

    filtered_attribute_distribution_list = []
    for attribute_distribution in attribute_distribution_list:
        filter_one = {}
        for k, v in attribute_distribution.items():
            if k in limit_fields_dict:
                filter_one[k] = v
        filtered_attribute_distribution_list.append(filter_one)
    return filtered_attribute_distribution_list





def random_sample_one_from_attribute_distribute_list(attribute_distribution_list):
    if attribute_distribution_list is None:
        return None
    if len(attribute_distribution_list) == 0:
        return None
    attribute_item = np.random.choice(attribute_distribution_list)
    return attribute_item


def attempt_override_attribute(render_attribute, attribute_distribution_list):
    override_attribute_dict = random_sample_one_from_attribute_distribute_list(attribute_distribution_list)
    if override_attribute_dict is not None:
        render_attribute = override_attribute_with_given_dict(render_attribute, override_attribute_dict)

    return render_attribute

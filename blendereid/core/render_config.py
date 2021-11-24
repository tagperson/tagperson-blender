import os
import bpy
import random


def compose_output_dir(cfg):
    if cfg.OUTPUT_DIR_FOR_IMAGE != '':
        output_dir = cfg.OUTPUT_DIR_FOR_IMAGE
    else:
        output_dir = os.path.join(cfg.OUTPUT_DIR, "output_persons")
    return output_dir

def generate_save_path(cfg, mesh_id, camera_index, sequence_id):
    output_dir = compose_output_dir(cfg)
    save_name = f"{mesh_id}_c{camera_index}s1_{int(sequence_id)}.jpg"
    save_path = f"{output_dir}/{save_name}"
    return save_path


def setup_basic_render(cfg):
    render = bpy.data.scenes['Scene'].render
    render.resolution_x = 128
    render.resolution_y = 256
    render.resolution_percentage = 50
    bpy.context.scene.cycles.samples = 8
    # render.tile_x = 8
    # render.tile_y = 8
    render.film_transparent = True
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.image_settings.file_format='JPEG'


def modify_render_config(cfg):
    # TODO: modify to `modify_render_config_v2` logic, modify render by given params
    render = bpy.data.scenes['Scene'].render
    render.resolution_x = get_random_resolution_x(cfg)
    render.resolution_y = get_random_resolution_y(cfg, render.resolution_x)
    render.resolution_percentage = get_random_resolution_percentage(cfg)

def get_random_resolution_x(cfg):
    resolution_x = cfg.RENDER.RESOLUTION_X.BASE + random.randint(cfg.RENDER.RESOLUTION_X.RANDOM_LOWER_BOUND, cfg.RENDER.RESOLUTION_X.RANDOM_UPPER_BOUND)
    return resolution_x
def get_random_resolution_y(cfg, resolution_x):
    if not cfg.RENDER.RESOLUTION_Y.USE_RATIO.ENABLED:
        resolution_y = cfg.RENDER.RESOLUTION_Y.BASE + random.randint(cfg.RENDER.RESOLUTION_Y.RANDOM_LOWER_BOUND, cfg.RENDER.RESOLUTION_Y.RANDOM_UPPER_BOUND)
    else:
        y_ratio = random.uniform(cfg.RENDER.RESOLUTION_Y.USE_RATIO.RANDOM_LOWER_BOUND, cfg.RENDER.RESOLUTION_Y.USE_RATIO.RANDOM_UPPER_BOUND)
        resolution_y = int(resolution_x * y_ratio)
    return resolution_y
def get_random_resolution_percentage(cfg):
    resolution_percentage = cfg.RENDER.RESOLUTION_PERCENTAGE.BASE + random.randint(cfg.RENDER.RESOLUTION_PERCENTAGE.RANDOM_LOWER_BOUND, cfg.RENDER.RESOLUTION_PERCENTAGE.RANDOM_UPPER_BOUND)
    return resolution_percentage

def modify_render_config_by_bg_image(cfg, bg_image_name, bg_image_info):
    # TODO: modify to `modify_render_config_v2` logic, modify render by given params
    """
    20210628 modify render image x, y and percentage by it's bg_image_name
    The purpose is to ensure same bg_image_name appear at same resolution parameters
    """
    render = bpy.data.scenes['Scene'].render
    if bg_image_info is None or bg_image_name not in bg_image_info:
        print(f"Warning: bg_image_name `{bg_image_name}` not found...")
        render.resolution_x = get_random_resolution_x(cfg)
        render.resolution_y = get_random_resolution_y(cfg, render.resolution_x)
        render.resolution_percentage = get_random_resolution_percentage(cfg)
    else:
        render.resolution_x = bg_image_info[bg_image_name]['x']
        render.resolution_y = bg_image_info[bg_image_name]['y']
        render.resolution_percentage = bg_image_info[bg_image_name]['p']


def get_random_render_resolution(cfg):
    resolution_x = get_random_resolution_x(cfg)
    resolution_y = get_random_resolution_y(cfg, resolution_x)
    resolution_percentage = get_random_resolution_percentage(cfg)
    return resolution_x, resolution_y, resolution_percentage


def get_random_render_resolution_by_bg_image(cfg, bg_image_name, bg_image_info):
    if bg_image_info is None or bg_image_name not in bg_image_info:
        print(f"Warning: bg_image_name `{bg_image_name}` not found...")
        return get_random_render_resolution(cfg)
    else:
        resolution_x = bg_image_info[bg_image_name]['x']
        resolution_y = bg_image_info[bg_image_name]['y']
        resolution_percentage = bg_image_info[bg_image_name]['p']
        return resolution_x, resolution_y, resolution_percentage


def modify_render_config_v2(resolution_x, resolution_y, resolution_percentage):
    render = bpy.data.scenes['Scene'].render
    render.resolution_x = resolution_x
    render.resolution_y = resolution_y
    render.resolution_percentage = resolution_percentage


def enable_cuda_render():
    """
    There has some bugs, it slow down the render
    """
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    bpy.data.scenes['Scene'].cycles.device = 'GPU'

    # Enable and list all devices, or optionally disable CPU
    print("----------------------------------------------")
    for devices in bpy.context.preferences.addons['cycles'].preferences.get_devices():
        for d in devices:
            d.use = True
            # if d.type == 'CPU':
            #     d.use = False
            print("Device '{}' type {} : {}" . format(d.name, d.type, d.use))
    print("----------------------------------------------")

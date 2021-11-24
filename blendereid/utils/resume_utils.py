import glob
import os

from blendereid.core import render_config

def check_rendering_result_exist(cfg, current_mesh_id):
    if cfg.PROCESS.IMAGE_COUNT_PER_ID_RANDOM_LOWER_BOUND !=0 or cfg.PROCESS.IMAGE_COUNT_PER_ID_RANDOM_UPPER_BOUND != 0:
        print(f"config is using dynamic IMAGE_COUNT_PER_ID, could not check whether it rendered.")
        return False

    output_dir = render_config.compose_output_dir(cfg)
    mesh_save_path_pattern = os.path.join(output_dir, f"{current_mesh_id}_c*s1_*.jpg")
    mesh_path = glob.glob(mesh_save_path_pattern)
    if len(mesh_path) == cfg.PROCESS.IMAGE_COUNT_PER_ID:
        return True
    
    return False
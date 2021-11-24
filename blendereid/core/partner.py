import numpy as np
from blendereid.utils import mesh_utils, geometry
import os
import random

def random_select_one_partner(cfg):
    random_min = cfg.PARTNER.SELECT_MESH_ID_MIN
    random_max = cfg.PARTNER.SELECT_MESH_ID_MAX
    partner_mesh_id = np.random.randint(random_min, random_max)
    partner_mesh_file_name = mesh_utils.format_mesh_file_name(partner_mesh_id, cfg.SOURCE.OBJ_POSE_NAME, suffix="mhx2")
    partner_obj_file_path = os.path.join(cfg.SOURCE.ROOT, partner_mesh_file_name)
    return partner_obj_file_path


def set_partner_location_and_rotation(cfg, person_location, partner_obj_person, azim):
    opposite_azim = (azim + 180) % 360
    relative_azim = random.randint(-45, 45)
    target_azim = opposite_azim + relative_azim
    distance = random.uniform(4, 6) + (45 - abs(relative_azim)) * 0.1

    elev = 0
    partner_obj_person.location = geometry.calculate_target_location(person_location, distance, target_azim, 0)
    if random.random() < 0.5:
        partner_obj_person.rotation_euler.z = random.uniform(-0.5, 0.5)
    else:
        partner_obj_person.rotation_euler.z = random.uniform(2.64, 3.64)
    
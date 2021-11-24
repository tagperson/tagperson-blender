import random

def get_random_light_azim(cfg, camera_azim):
    light_azim = (camera_azim + random.randint(cfg.LIGHT.AZIM.RANDOM_LOWER_BOUND, cfg.LIGHT.AZIM.RANDOM_UPPER_BOUND)) % 360
    return light_azim

def get_random_light_elev(cfg, camera_elev):
    light_elev_base = cfg.LIGHT.ELEV.BASE
    light_elev_random = 0
    if cfg.LIGHT.ELEV.RANDOM.ENABLED:
        if cfg.LIGHT.ELEV.RANDOM.USE_GAUSS:
            light_elev_random = random.gauss(cfg.LIGHT.ELEV.RANDOM.MU, cfg.LIGHT.ELEV.RANDOM.SIGMA)
        else:
            light_elev_random = random.randint(cfg.LIGHT.ELEV.RANDOM.LOWER_BOUND, cfg.LIGHT.ELEV.RANDOM.UPPER_BOUND)
    
    light_elev = light_elev_base + light_elev_random
    return light_elev

def get_random_light_distance(cfg, camera_distance):
    light_distance = camera_distance * cfg.LIGHT.DISTANCE.RATIO_TO_CAMERA_DISTANCE
    return light_distance
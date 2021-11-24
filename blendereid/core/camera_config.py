import random


def adjust_camera_roration(obj_camera, obj_person, cfg, elev=10, distance=25):

    camera_rotation_euler_x_bias = cfg.CAMERA.ROTATION_EULER_X_BIAS.BIAS
    if cfg.CAMERA.OCCATIONAL_JUMP.ENABLE:
        if random.random() < cfg.CAMERA.OCCATIONAL_JUMP.PROB:
            camera_rotation_euler_x_bias = cfg.CAMERA.OCCATIONAL_JUMP.ROTATION_EULER_X_BIAS.BIAS

    # camera_rotation_euler_x_bias += max(0, elev-10) / 1000
    camera_rotation_euler_x_bias += 0.01 - max(0, 28 - obj_person.dimensions[2]) / 2000 * (elev - 10) / 7
    # camera_rotation_euler_x_bias -= max(0, distance-25) / 200
    if cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_x_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.SIGMA)
        else:
            # camera_rotation_euler_x_bias += (random.random() + cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.BIAS - 0.5) * cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.SCALE
            camera_rotation_euler_x_bias += random.uniform(cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.LOWER_BOUND, cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.UPPER_BOUND)

    camera_rotation_euler_z_bias = cfg.CAMERA.ROTATION_EULER_Z_BIAS.BIAS
    if cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_z_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.SIGMA)
        else:
            # camera_rotation_euler_z_bias += (random.random() + cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.BIAS - 0.5) * cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.SCALE
            camera_rotation_euler_z_bias += random.uniform(cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.LOWER_BOUND, cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.UPPER_BOUND)

    camera_rotation_euler_y_bias = cfg.CAMERA.ROTATION_EULER_Y_BIAS.BIAS
    if cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_y_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.SIGMA)


    obj_pose = obj_person.matrix_world.to_translation()
    camera_pos = obj_camera.matrix_world.to_translation()
    direction = obj_pose - camera_pos
    # obj_pose the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    obj_camera.rotation_euler.x += camera_rotation_euler_x_bias
    obj_camera.rotation_euler.z += camera_rotation_euler_z_bias
    obj_camera.rotation_euler.y += camera_rotation_euler_y_bias
    # print(f"object pos: {obj_pose}, camera: {camera_pos}")
    # print(f"direction: {direction}")
    # print(f"rot_quat: {rot_quat}")
    # print(f"rotation_euler: {obj_camera.rotation_euler}")

    return camera_rotation_euler_x_bias, camera_rotation_euler_y_bias, camera_rotation_euler_z_bias
    

def get_random_camera_elev(cfg):
    elev = cfg.CAMERA.ELEV.BASE
    if cfg.CAMERA.ELEV.RANDOM.ENABLED == True:
        if not cfg.CAMERA.ELEV.RANDOM.USE_GAUSS:
            elev += random.randint(cfg.CAMERA.ELEV.RANDOM.LOWER_BOUND, cfg.CAMERA.ELEV.RANDOM.UPPER_BOUND)
        else:
            elev = random.gauss(cfg.CAMERA.ELEV.RANDOM.MU, cfg.CAMERA.ELEV.RANDOM.SIGMA)

    return elev

def get_random_camera_azim(cfg):
    azim = random.randint(0, 360)
    return azim

def get_random_camera_distance(cfg, elev, obj_person):
    distance = (0.2 + cfg.CAMERA.DISTANCE.PERSON_HEIGHT_FACTOR * obj_person.dimensions[2]) + random.uniform(cfg.CAMERA.DISTANCE.RANDOM.LOWER_BOUND, cfg.CAMERA.DISTANCE.RANDOM.UPPER_BOUND) # for mhx2
    cur_distance = distance + float(elev - 10) * 0.12 * (1+(max(0, obj_person.dimensions[2] - 15) / 100))
    return cur_distance

def get_adjusted_camera_rotation(cfg, obj_person, elev):
    
    camera_rotation_euler_x_bias = cfg.CAMERA.ROTATION_EULER_X_BIAS.BIAS
    camera_rotation_euler_x_bias += 0.01 - max(0, 28 - obj_person.dimensions[2]) / 2000 * (elev - 10) / 7
    if cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_x_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.SIGMA)
        else:
            camera_rotation_euler_x_bias += random.uniform(cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.LOWER_BOUND, cfg.CAMERA.ROTATION_EULER_X_BIAS.RANDOM.UPPER_BOUND)

    camera_rotation_euler_z_bias = cfg.CAMERA.ROTATION_EULER_Z_BIAS.BIAS
    if cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_z_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.SIGMA)
        else:
            # camera_rotation_euler_z_bias += (random.random() + cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.BIAS - 0.5) * cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.SCALE
            camera_rotation_euler_z_bias += random.uniform(cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.LOWER_BOUND, cfg.CAMERA.ROTATION_EULER_Z_BIAS.RANDOM.UPPER_BOUND)

    camera_rotation_euler_y_bias = cfg.CAMERA.ROTATION_EULER_Y_BIAS.BIAS
    if cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.ENABLE:
        if cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.USE_GAUSS:
            camera_rotation_euler_y_bias += random.gauss(cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.MU, cfg.CAMERA.ROTATION_EULER_Y_BIAS.RANDOM.SIGMA)
    
    return camera_rotation_euler_x_bias, camera_rotation_euler_y_bias, camera_rotation_euler_z_bias

def set_camera_roration(obj_camera, obj_person, cre_x_bias=0.0, cre_y_bias=0.0, cre_z_bias=0.0):
    
    position_person = obj_person.matrix_world.to_translation()
    position_camera = obj_camera.matrix_world.to_translation()
    direction = position_person - position_camera
    # position_person the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    obj_camera.rotation_euler.x += cre_x_bias
    obj_camera.rotation_euler.z += cre_z_bias
    obj_camera.rotation_euler.y += cre_y_bias

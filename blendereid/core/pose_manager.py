import numpy as np
import os
import random

def fetch_pose_names(cfg, frame_count):
    pose_root = cfg.POSE.ROOT
    # pose_serial_candidates = ['02_01', '02_02', '02_03', '02_04', '02_05']
    # pose_serial_candidates = ['02_01', '02_02', '02_03']
    pose_serial_candidates = cfg.POSE.SERIALS
    # pose_serial_candidates = ['walk']
    pose_serials = np.random.choice(pose_serial_candidates, 2)

    # first_count = random.randint(int(0.3 * frame_count), int(0.7 * frame_count))
    # cur_pose_root = os.path.join(pose_root, pose_serials[0])
    # first_pose_candidates = os.listdir(cur_pose_root)
    # # first_pose_candidates = sorted(first_pose_candidates)
    # first_pose_names = np.random.choice(first_pose_candidates, first_count)
    # first_pose_names = [f'{pose_serials[0]}/{first_pose_name}' for first_pose_name in first_pose_names]

    # second_count = frame_count - first_count
    # cur_pose_root = os.path.join(pose_root, pose_serials[1])
    # second_pose_candidates = os.listdir(cur_pose_root)
    # # second_pose_candidates = sorted(second_pose_candidates)
    # second_pose_names = np.random.choice(second_pose_candidates, second_count)
    # second_pose_names = [f'{pose_serials[1]}/{second_pose_name}' for second_pose_name in second_pose_names]

    # first_pose_names.extend(second_pose_names)

    # return first_pose_names

    pose_candidates = []
    for pose_serial in pose_serial_candidates:
        cur_pose_root = os.path.join(pose_root, pose_serial)
        p_candidates = os.listdir(cur_pose_root)
        p_candidates = sorted(p_candidates)
        p_candidates = [f"{pose_serial}/{p_candidate}" for p_candidate in p_candidates]
        pose_candidates.extend(p_candidates)
    pose_names = np.random.choice(pose_candidates, frame_count)
    return pose_names


def find_adjacent_pose_path(pose_path):
    pose_dir = os.path.dirname(pose_path)
    pose_name = os.path.basename(pose_path)
    pure_pose_name = os.path.splitext(pose_name)[0]
    pose_info = pure_pose_name.split("_")
    pose_name_seq = pose_info[2]
    pose_name_seq = int(pose_name_seq)
    add_num = random.randint(1, 5)
    # assume the seq is in 2-50
    next_pose_seq = (pose_name_seq + add_num) % 50
    if next_pose_seq < 2:
        next_pose_seq += 2
        
    next_pose_name = f"{pose_info[0]}_{pose_info[1]}_{next_pose_seq}.json"
    next_pose_path = os.path.join(pose_dir, next_pose_name)
    return next_pose_path


def apply_transform_to_bones(obj_person):
    obj_person.keyframe_insert(data_path='location')
    # apply keyframe on person's bone pose
    for bone in obj_person.pose.bones:
        bone.keyframe_insert(data_path = 'location')
        if bone.rotation_mode == "QUATERNION":
            bone.keyframe_insert(data_path = 'rotation_quaternion')
        else:
            bone.keyframe_insert(data_path = 'rotation_euler')
        bone.keyframe_insert(data_path = 'scale')


def fetch_pose_paths_in_one_camera(cfg, frame_count):
    pose_root = cfg.POSE.ROOT
    pose_serial_candidates = cfg.POSE.SERIALS
    pose_serials = np.random.choice(pose_serial_candidates, 1)
    cur_pose_root = os.path.join(pose_root, pose_serials[0])
    pose_candidates = os.listdir(cur_pose_root)
    pose_candidates = sorted(pose_candidates)
    pose_candidates = [os.path.join(cur_pose_root, f"{p_candidate}") for p_candidate in pose_candidates]
    pose_path = np.random.choice(pose_candidates, frame_count)
    # TODO: sort pose_path
    return pose_path
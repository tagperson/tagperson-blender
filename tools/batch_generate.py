import bpy
from blendereid.config import get_cfg
from blendereid.utils import bpy_utils, misc
from blendereid.core import process

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='args parser for blender renderer.')
    parser.add_argument('--config-file', default='', help='')
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()
    return args


def setup(args):
    """
    Create configs and perform basic setups.
    """
    cfg = get_cfg()
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()
    # default_setup(cfg, args)
    return cfg

if __name__ == "__main__":
    
    bpy_utils.register_bpy_libs()
    bpy_utils.remove_object(obj_key='Cube')

    args = parse_args()
    print("Command Line Args:", args)
    cfg = setup(args)

    misc.fix_random_seeds(cfg.FIX_SEED + cfg.PROCESS.FIRST_INDEX - 1) # ensure diffrent seeds for start index
    process.generate_multiple_persons(cfg)
    
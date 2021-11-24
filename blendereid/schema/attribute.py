
class Attribute:
    mesh_id: int
    camera_azim: int
    camera_elev: int
    camera_distance: float
    light_azim: int
    light_elev: int
    light_distance: float
    background: str
    pose: str
    camera_idx: int
    img_width: int
    img_height: int
    partner_exist: bool
    partner_mesh_id_list: list
    cre_x_bias: float
    cre_y_bias: float
    cre_z_bias: float
    world_color: list
    world_color_to_background: list
    seq_idx: int
    img_shield_v2_name: list
    gamma_value: float

    # only use to render
    pose_path: str
    save_path: str

    def __init__(self, mesh_id, camera_azim, camera_elev, camera_distance, light_azim, light_elev, light_distance, background='', pose='', camera_idx=-1, img_width=0, img_height=0, partner_exist=False, partner_mesh_id_list=[], cre_x_bias=0.0, cre_y_bias=0.0, cre_z_bias=0.0, world_color=(0.0, 0.0, 0.0, 0.0), world_color_to_background=(0.0, 0.0, 0.0, 0.0), seq_idx=0, pose_path='', save_path='', img_shield_v2_name=[], gamma_value=None):
        self.mesh_id = mesh_id
        self.camera_azim = camera_azim
        self.camera_elev = camera_elev
        self.camera_distance = round(camera_distance, 3)
        self.light_azim = light_azim
        self.light_elev = light_elev
        self.light_distance = round(light_distance, 3)
        self.background = background
        self.pose = pose
        self.camera_idx = int(camera_idx)
        self.img_width = img_width
        self.img_height = img_height
        self.partner_exist = partner_exist
        self.partner_mesh_id_list = partner_mesh_id_list
        self.cre_x_bias = round(cre_x_bias, 3)
        self.cre_y_bias = round(cre_y_bias, 3)
        self.cre_z_bias = round(cre_z_bias, 3)
        self.world_color = world_color
        self.world_color_to_background = world_color_to_background
        self.seq_idx = int(seq_idx)
        self.img_shield_v2_name = img_shield_v2_name
        self.gamma_value = gamma_value
        
        self.pose_path = pose_path
        self.save_path = save_path

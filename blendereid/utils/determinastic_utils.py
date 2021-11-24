


def set_variable_according_to_determinastic_params(variable_value, variable_name: str, determinastic_params: dict):
    """
    camera_azim
    camera_elev
    camera_distance
    """
    if determinastic_params is None:
        return variable_value
    if variable_name not in determinastic_params:
        return variable_value
    
    return determinastic_params[variable_name]
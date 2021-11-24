
import math

def calculate_target_location(origin_location, distance, azimuth, elevation):
    """
    Given the origin point, distance, azimuth and elevation, find the target location
    azimuth ~ (0, 360]
    elevation ~ (0, 90]
    """

    assert len(origin_location) == 3
    
    # project to plane
    z = distance * math.sin(math.radians(elevation))
    plane_distance = distance * math.cos(math.radians(elevation))

    # suppose azimuth from the first quartile
    x = plane_distance * math.cos(math.radians(azimuth))
    y = plane_distance * math.sin(math.radians(azimuth))

    # find target location
    vec = (x, y, z)
    target_location = (origin_location[0] + vec[0], origin_location[1] + vec[1], origin_location[2] + vec[2])
    # print(f"target_location={target_location}")
    
    return target_location

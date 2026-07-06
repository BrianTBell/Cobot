import os
import yaml
import math

def load_joint_limits(yaml_path=None):
    """Quickly load in joint_limits from servo_params.yaml"""
    if yaml_path is None:
        yaml_path = os.path.join(os.path.dirname(__file__), "config/servo_params.yaml")

    with open(yaml_path) as f:
        params = yaml.safe_load(f)
    joints = params["cobot_control"]["ros__parameters"]["joints"]
    # order must match chain.links[1:5] -> Joint0..Joint3
    return [(math.radians(j["min_degrees"]), math.radians(j["max_degrees"]))
            for j in joints.values()]

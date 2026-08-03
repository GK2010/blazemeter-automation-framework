# This assumes Jenkins will always execute from the project root.
# import yaml

# def load_config():
#     with open("config/config.yaml","r") as file: 
#         return yaml.safe_load(file)


# As  Jenkins workspace paths can differ. Script should fail clearly if configuration is missing.
from pathlib import Path
import yaml


def load_config():

    config_path = Path("config/config.yaml")

    if not config_path.exists():
        raise FileNotFoundError(
            "Missing config/config.yaml"
        )

    with open(config_path, "r") as file:
        return yaml.safe_load(file)
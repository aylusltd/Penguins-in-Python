import yaml

inventory = {}

with open("configs/inventory.yaml", 'r') as stream:
    try:
        starting_inventory = yaml.safe_load(stream)
        # print starting_inventory
    except yaml.YAMLError as exc:
        print(exc)


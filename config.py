import json

def get_checkin_data():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            total = config.get('total_interview', 100)
            checked_in = config.get('number_of_checked_in', 0)
            npg = config.get('npg', 0)
            return total, checked_in, npg
    except Exception as e:
        print(f"Error reading config: {str(e)}")
        return 100, 0, 0

def update_config_npg(new_value):
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        config['npg'] = int(new_value) if new_value else 0
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=2)
        print(f"Updated config.json with npg: {config['npg']}")
    except Exception as e:
        print(f"Error updating config: {str(e)}")

def get_init_time():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            return config.get('init_time', 0)
    except Exception as e:
        print(f"Error reading init_time: {str(e)}")
        return 0

def update_config_init_time(new_value):
    from utils import datetime_to_excel
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
        config['init_time'] = datetime_to_excel(new_value) if new_value else 0
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=2)
        print(f"Updated config.json with init_time: {config['init_time']}")
    except Exception as e:
        print(f"Error updating init_time: {str(e)}")
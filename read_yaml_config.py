
#read_yaml_config.py
import yaml

def read_yaml_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except yaml.YAMLError as exc:
        print(f"Error: Invalid YAML syntax. Details: {exc}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Usage
if __name__ == "__main__":
    config = read_yaml_config('synthetic_monitoring_config.yaml')
    if config:
        print("YAML configuration successfully loaded.")

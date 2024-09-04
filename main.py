import argparse
import yaml
from ping3 import ping
from prometheus_client import start_http_server, Gauge
import time


# Define Prometheus metrics
response_time = Gauge('ping_response_time_seconds', 'Response time of the ping', ['target'])
packet_loss = Gauge('ping_packet_loss_rate', 'Packet loss rate of the ping', ['target'])


def parse_arguments():
    parser = argparse.ArgumentParser(description="Synthetic monitoring with YAML configuration.")
    parser.add_argument('config_path', type=str, nargs='?', default='synthetic_monitoring_config.yaml',
                        help='Path to the YAML configuration file (default: synthetic_monitoring_config.yaml).')
    return parser.parse_args()


def read_yml(file_path):
    """
    Reads a YAML configuration file and returns the parsed data.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def update_metrics(servers, interval):
    while True:
        for server in servers:
            destination = server['destination']
            print(f"Pinging {server['name']} ({destination})...")

            # Ping the server and measure response time
            response = ping(destination, timeout=2)  # timeout of 2 seconds per ping
            if response is None:
                # If ping fails, assume 100% packet loss
                print(f"Ping failed for {server['name']} ({destination})")
                response_time.labels(server['name']).set(0)
                packet_loss.labels(server['name']).set(100.0)
            else:
                # If ping is successful, update metrics
                print(f"Ping successful for {server['name']} ({destination}) - Response time: {response} seconds")
                response_time.labels(server['name']).set(response)
                packet_loss.labels(server['name']).set(0.0)  # Assume 0% packet loss for a successful ping

            # Print metrics to the console
            print(f"Metrics for {server['name']}: Response Time = {response} seconds, Packet Loss = {packet_loss.labels(server['name'])._value.get()}%")

        time.sleep(interval)


def main():
    args = parse_arguments()
    config = read_yml(args.config_path)

    servers = config.get('servers', [])
    interval = config.get('interval', 10)  # Default to 10 seconds

    # Start Prometheus HTTP server
    print("Starting Prometheus metrics server on port 8989...")
    start_http_server(8989)

    # Start updating metrics
    print("Starting synthetic monitoring...")
    update_metrics(servers, interval)


if __name__ == "__main__":
    main()


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
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def calculate_metrics(server, probes, packet_count):
    destination = server['ip']
    total_time = 0.0
    successful_pings = 0

    for _ in range(probes):
        for _ in range(packet_count):
            response = ping(destination)
            if response:
                total_time += response
                successful_pings += 1
            print (calculate_metrics)
    if successful_pings > 0:
        avg_time = total_time / successful_pings
        packet_loss_rate = 100.0 * (1 - successful_pings / (probes * packet_count))
    else:
        avg_time = None
        packet_loss_rate = 100.0

    return {
        'avg_time': avg_time,
        'packet_loss_rate': packet_loss_rate
    }


def update_metrics(servers, interval, probes, packet_count):
    while True:
        for server in servers:
            print(f"Pinging {server['name']} ({server['ip']}) with {probes} probes and {packet_count} packets per probe...")

            metrics = calculate_metrics(server, probes, packet_count)

            # Update Prometheus metrics
            if metrics['avg_time'] is not None:
                response_time.labels(server['name']).set(metrics['avg_time'])
            else:
                response_time.labels(server['name']).set(0)
            packet_loss.labels(server['name']).set(metrics['packet_loss_rate'])

            # Print metrics to the console
            print(f"Metrics for {server['name']}: {metrics}")

        time.sleep(interval)


def main():
    args = parse_arguments()
    config = read_yml(args.config_path)

    servers = config['monitoring_targets']['servers']
    interval = config['monitoring_config']['time_interval']
    probes = config['monitoring_config']['probes']
    packet_count = config['monitoring_config']['packet_count']

    # Start Prometheus HTTP server
    print("Starting Prometheus metrics server on port 8989...")
    start_http_server(8989)

    # Start updating metrics
    print("Starting synthetic monitoring...")
    update_metrics(servers, interval, probes, packet_count)


if __name__ == "__main__":
    main()


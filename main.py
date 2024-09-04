import argparse
import yaml
import time
from prometheus_client import start_http_server, Gauge
import pingparsing
import concurrent.futures

# Initialize Prometheus metrics
packet_transmit = Gauge("packet_transmit", "Packets transmitted", ["server"])
packet_receive = Gauge("packet_receive", "Packets received", ["server"])
packet_loss_rate = Gauge("packet_loss_rate", "Packet loss rate", ["server"])
rtt_min = Gauge("rtt_min", "Round trip time min in milliseconds", ["server"])
rtt_avg = Gauge("rtt_avg", "Round trip time avg in milliseconds", ["server"])
rtt_max = Gauge("rtt_max", "Round trip time max in milliseconds", ["server"])
rtt_mdev = Gauge("rtt_mdev", "Round trip time standard deviation", ["server"])
ping_success_rate = Gauge("ping_success_rate", "Ping success rate", ["server"])

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

def ping_parse(destination, interval, probes, packet_count):
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = destination

    successful_pings = 0
    total_pings = 0

    while True:
        for _ in range(probes):
            ping_results = ping_parser.parse(transmitter.ping())
            icmp_replies_list = ping_results.icmp_replies

            total_pings += 1
            if ping_results.packet_receive > 0:
                successful_pings += 1

            ping_data = {
                "packet_transmit": ping_results.packet_transmit,
                "packet_receive": ping_results.packet_receive,
                "packet_loss_rate": ping_results.packet_loss_rate,
                "rtt_min": ping_results.rtt_min,
                "rtt_avg": ping_results.rtt_avg,
                "rtt_max": ping_results.rtt_max,
                "rtt_mdev": ping_results.rtt_mdev,
            }

            # Set the metric values
            packet_transmit.labels(server=destination).set(ping_data["packet_transmit"])
            packet_receive.labels(server=destination).set(ping_data["packet_receive"])
            packet_loss_rate.labels(server=destination).set(ping_data["packet_loss_rate"])
            rtt_min.labels(server=destination).set(ping_data["rtt_min"])
            rtt_avg.labels(server=destination).set(ping_data["rtt_avg"])
            rtt_max.labels(server=destination).set(ping_data["rtt_max"])
            rtt_mdev.labels(server=destination).set(ping_data["rtt_mdev"])

            success_rate = (successful_pings / total_pings) * 100
            ping_success_rate.labels(server=destination).set(success_rate)

        time.sleep(interval)

def main():
    args = parse_arguments()
    config = read_yml(args.config_path)

    servers = config.get('monitoring_targets', {}).get('servers', [])
    interval = config.get('monitoring_config', {}).get('time_interval', 60)
    probes = config.get('monitoring_config', {}).get('probes', 3)
    packet_count = config.get('monitoring_config', {}).get('packet_count', 4)

    # Start Prometheus HTTP server
    print("Starting Prometheus metrics server on port 8989...")
    start_http_server(8989)

    # Start updating metrics
    print("Starting synthetic monitoring...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for server in servers:
            destination = server.get('ip')
            if destination:
                executor.submit(ping_parse, destination, interval, probes, packet_count)

if __name__ == "__main__":
    main()

import psutil


def monitor_network_traffic(interval=1):
    """Surveille le trafic réseau toutes les `interval` secondes et affiche les octets reçus et envoyés."""
    prev_counters = psutil.net_io_counters()
    while True:
        time.sleep(interval)
        counters = psutil.net_io_counters()
        sent = counters.bytes_sent - prev_counters.bytes_sent
        recv = counters.bytes_recv - prev_counters.bytes_recv
        print(f"Sent: {sent} bytes, Received: {recv} bytes in the last {interval} seconds")
        prev_counters = counters

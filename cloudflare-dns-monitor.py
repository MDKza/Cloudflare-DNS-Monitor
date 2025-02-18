import json
import requests
import subprocess
import time
import logging

# Load configuration from JSON file
def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

config = load_config()

# Configure logging with dynamic log level
log_level = getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO)
logging.basicConfig(filename="cloudflare_monitor.log", level=log_level,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ping_host(host, count):
    """Ping a host a specified number of times."""
    try:
        result = subprocess.run(["ping", "-n", str(count), host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success = result.returncode == 0
        logging.debug(f"Ping output for {host}: {result.stdout.decode(errors='ignore')}")
        logging.info(f"Ping {host}: {'Success' if success else 'Failure'}")
        return success
    except Exception as e:
        logging.error(f"Error pinging {host}: {e}")
        return False

def get_dns_records():
    """Retrieve DNS records from Cloudflare."""
    try:
        headers = {"Authorization": f"Bearer {config['cloudflare']['api_token']}", "Content-Type": "application/json"}
        response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{config['cloudflare']['zone_id']}/dns_records", headers=headers)
        response.raise_for_status()
        logging.debug(f"Cloudflare DNS Records Response: {response.json()}")
        logging.info("Retrieved DNS records from Cloudflare.")
        return response.json().get("result", [])
    except Exception as e:
        logging.error(f"Error retrieving DNS records: {e}")
        return []

def update_dns_record(action, dns_entry, ip):
    """Update Cloudflare DNS record by adding or removing an IP."""
    try:
        headers = {"Authorization": f"Bearer {config['cloudflare']['api_token']}", "Content-Type": "application/json"}
        records = get_dns_records()
        
        for record in records:
            if record["name"] == dns_entry and record["type"] == "A" and record["content"] == ip:
                record_id = record["id"]
                if action == "remove":
                    delete_url = f"https://api.cloudflare.com/client/v4/zones/{config['cloudflare']['zone_id']}/dns_records/{record_id}"
                    requests.delete(delete_url, headers=headers)
                    logging.info(f"Removed DNS record {dns_entry} -> {ip}")
                return
        
        if action == "add":
            add_url = f"https://api.cloudflare.com/client/v4/zones/{config['cloudflare']['zone_id']}/dns_records"
            data = {"type": "A", "name": dns_entry, "content": ip, "ttl": config['cloudflare']['ttl'], "proxied": config['cloudflare']['proxied']}
            requests.post(add_url, json=data, headers=headers)
            logging.info(f"Added DNS record {dns_entry} -> {ip}")
    except Exception as e:
        logging.error(f"Error updating DNS record ({action}) for {dns_entry} -> {ip}: {e}")

def monitor():
    """Monitor the given destinations and update Cloudflare accordingly."""
    while True:
        try:
            logging.info("Starting monitoring cycle...")
            for dns_entry, records in config["dns_entries"].items():
                for ip, destinations in records.items():
                    logging.info(f"Checking IP: {ip} for DNS entry: {dns_entry}")
                    down_count = sum(not ping_host(host, config['ping']['count']) for host in destinations)
                    
                    if down_count >= config['ping']['fail_threshold']:
                        logging.warning(f"{ip} failed {down_count} pings, removing from DNS.")
                        update_dns_record("remove", dns_entry, ip)
                    else:
                        logging.info(f"{ip} is reachable, ensuring it's in DNS.")
                        update_dns_record("add", dns_entry, ip)
            
            logging.info(f"Monitoring cycle completed. Sleeping for {config['ping']['interval']} seconds.")
            time.sleep(config['ping']['interval'])
        except Exception as e:
            logging.critical(f"Critical error in monitoring function: {e}")
            time.sleep(10)  # Wait a bit before retrying

if __name__ == "__main__":
    logging.info("Starting Cloudflare DNS Monitor...")
    monitor()

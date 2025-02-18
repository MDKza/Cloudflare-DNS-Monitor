# Cloudflare DNS Monitor

## Overview
This script monitors the reachability of IP addresses associated with Cloudflare DNS A records. If an IP becomes unreachable, the script removes it from Cloudflare. When it becomes reachable again, the script re-adds it.

## Features
- Monitors multiple DNS A records.
- Pings up to 4 target IPs per A record.
- Removes DNS records from Cloudflare when ping failures exceed a threshold.
- Re-adds DNS records when connectivity is restored.
- Configurable settings via a `config.json` file.
- Supports logging with adjustable log levels.
- Runs continuously as a background process.

## Requirements
- Python 3.x
- `requests` module
- Cloudflare API credentials

## Installation
### **1. Install Dependencies**
```bash
pip install requests
```

### **2. Set Up `config.json`**
Create a `config.json` file in the same directory as the script and populate it with the following structure:

```json
{
    "cloudflare": {
        "api_token": "your_cloudflare_api_token",
        "zone_id": "your_cloudflare_zone_id",
        "ttl": 1,
        "proxied": false
    },
    "ping": {
        "count": 3,
        "fail_threshold": 2,
        "interval": 60
    },
    "logging": {
        "level": "INFO"
    },
    "dns_entries": {
        "test.example.com": {
            "a.a.a.a": ["4.2.2.1", "76.76.2.0", "9.9.9.9", "208.67.222.222"],
            "b.b.b.b": ["4.2.2.2", "76.76.10.0", "149.112.112.112", "208.67.220.220"]
        }
    }
}
```

## Configuration Options

### **1. Cloudflare API Settings**
| Key        | Type    | Description |
|-----------|--------|-------------|
| `api_token` | `string` | Cloudflare API token for authentication. |
| `zone_id`   | `string` | Cloudflare Zone ID where the DNS records exist. |
| `ttl`       | `integer` | TTL for the DNS records (`1` = automatic). |
| `proxied`   | `boolean` | Whether Cloudflare proxying should be enabled (`true` or `false`). |

### **2. Ping Monitoring Settings**
| Key             | Type    | Description |
|---------------|--------|-------------|
| `count`        | `integer` | Number of ping attempts per host. |
| `fail_threshold` | `integer` | Number of failed hosts before marking a DNS record as down. |
| `interval`     | `integer` | Time in seconds to wait between monitoring cycles. |

### **3. Logging Settings**
| Key        | Type    | Description |
|-----------|--------|-------------|
| `level`    | `string` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |

### **4. DNS Entries to Monitor**
This section defines which DNS entries should be monitored and which IPs they should resolve to.

```json
"dns_entries": {
    "test.example.com": {
        "a.a.a.a": ["4.2.2.1", "76.76.2.0", "9.9.9.9", "208.67.222.222"],
        "b.b.b.b": ["4.2.2.2", "76.76.10.0", "149.112.112.112", "208.67.220.220"]
    }
}
```
- **`test.example.com`** is the monitored domain.
- **`a.a.a.a`** and **`b.b.b.b`** are A records for the domain.
- The script pings the associated IPs to determine their reachability.

## Running the Script
To start the script, run:
```bash
python cloudflare-dns-monitor.py
```

### **Running on Reboot**

#### **On Windows (Task Scheduler)**
1. Open **Task Scheduler** (`Win + R`, type `taskschd.msc`, press Enter).
2. Click **Create Basic Task**.
3. Select **When the computer starts**.
4. Select **Start a program**, then browse for `python.exe`.
5. In the **Add arguments** field, enter:
   ```
   "C:\Path\To\cloudflare-dns-monitor.py"
   ```
6. Click **Finish**.

#### **On Linux (Systemd Service)**
1. Create a new systemd service:
   ```bash
   sudo nano /etc/systemd/system/cloudflare-monitor.service
   ```
2. Add the following content:
   ```ini
   [Unit]
   Description=Cloudflare DNS Monitor
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/cloudflare-dns-monitor.py
   Restart=always
   User=yourusername

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable the service:
   ```bash
   sudo systemctl enable cloudflare-monitor
   sudo systemctl start cloudflare-monitor
   ```

## Logging Levels
You can adjust the logging level in `config.json` under the `logging` section:
```json
"logging": {
    "level": "DEBUG"
}
```

### **Logging Breakdown**
| Level     | Description |
|-----------|-------------|
| `DEBUG`   | Full details, including API responses and ping results. |
| `INFO`    | Standard monitoring logs, including successful pings and DNS updates. |
| `WARNING` | Logs when an IP reaches the failure threshold. |
| `ERROR`   | Logs API failures and network errors. |
| `CRITICAL` | Logs fatal issues preventing execution. |

## Example Logs
```
2025-02-18 15:00:10,500 - INFO - Starting monitoring cycle...
2025-02-18 15:00:11,600 - INFO - Ping 4.2.2.1: Success
2025-02-18 15:00:12,700 - WARNING - a.a.a.a failed 2 pings, removing from DNS.
2025-02-18 15:00:14,900 - ERROR - Error updating DNS record (add) for test.example.com -> a.a.a.a: Cloudflare API error
```

## Troubleshooting
- **Cloudflare API errors?** Ensure your `api_token` and `zone_id` are correct.
- **Ping failures?** Check if the destination IPs are reachable manually using `ping`.
- **Script not running?** Ensure it is running via Task Scheduler (Windows) or `systemctl` (Linux).

## Contributing
Feel free to open an issue or submit a pull request for improvements.

## License
MIT License. Free to use and modify.


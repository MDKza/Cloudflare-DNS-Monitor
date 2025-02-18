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
- Required Python modules:
  ```bash
  pip install requests json logging subprocess
  ```
- Cloudflare API credentials

## Installation
### **1. Install Dependencies**
```bash
pip install requests json logging subprocess
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
            "a.a.a.a": {
                "ping_targets": ["4.2.2.1", "76.76.2.0", "9.9.9.9", "208.67.222.222"],
                "comment": "Primary server for test.example.com"
            },
            "b.b.b.b": {
                "ping_targets": ["4.2.2.2", "76.76.10.0", "149.112.112.112", "208.67.220.220"],
                "comment": "Backup server for test.example.com"
            }
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
        "a.a.a.a": {
            "ping_targets": ["4.2.2.1", "76.76.2.0", "9.9.9.9", "208.67.222.222"],
            "comment": "Primary server for test.example.com"
        },
        "b.b.b.b": {
            "ping_targets": ["4.2.2.2", "76.76.10.0", "149.112.112.112", "208.67.220.220"],
            "comment": "Backup server for test.example.com"
        }
    }
}
```
- **`test.example.com`** is the monitored domain.
- **`a.a.a.a`** and **`b.b.b.b`** are A records for the domain.
- Each A record includes:
  - **`ping_targets`**: List of IPs that will be pinged to determine reachability.
  - **`comment`**: Descriptive metadata for this record.

## Running the Script
To start the script, run:
```bash
python cloudflare_dns_monitor.py
```

## Logging Levels
You can adjust the logging level in `config.json` under the `logging` section:
```json
"logging": {
    "level": "DEBUG"
}
```

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

## License
MIT License. Free to use and modify.


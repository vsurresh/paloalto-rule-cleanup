For more information and detailed explanation - https://www.packetswitch.co.uk/trying-to-automate-palo-alto-firewall-objects-rules-cleanup/

# Palo Alto Firewall Object and Rule Cleanup Automation

This repository contains scripts for automating the cleanup of Palo Alto firewall objects and rules. When decommissioning servers or entire subnets, it can be cumbersome to remove associated objects and rules from the firewall manually. This automation script simplifies that process.

# Prerequisites
- The script targets Panorama. If you intend to work directly with individual firewalls, you might need to adjust the script.

Note: This script does not automatically commit or push changes. Ensure to do this manually via the GUI after reviewing changes.
As always, exercise caution. Confirm that only the intended configurations are being removed before committing any changes. Use this script at your own risk.

# How to Use
- Device Groups Configuration: In the main.py script, replace the device_groups dictionary with your own device groups.
- Specify Hosts/Subnets: Replace the hosts list in the main.py script with the subnets or hosts you wish to target for cleanup.
- Panorama Configuration: Update the pan_object instantiation in the main.py script with your Panorama's IP or FQDN.
- Credentials Setup: Set your Panorama username and password as environment variables before running the script.

```
export username=YOUR_USERNAME
export password=YOUR_PASSWORD
```


# Conclusion
This script simplifies the process of cleaning up objects and rules from your Palo Alto firewall setup. We welcome feedback and suggestions to enhance the utility of this tool.

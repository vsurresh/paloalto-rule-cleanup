import os
from paloaltoapi import PaloAltoAPI
import ipaddress
import json
import socket
import copy

device_groups = {
    "branch_offices": "PreRules",
    "head_office": "PreRules"
}

def is_valid_ip(ip_str):
    try:
        ipaddress.ip_network(ip_str, strict=False)
        return True
    except:
        return False

def process_addr_objects(address_obj, subnet):
    try:
        if 'ip-netmask' in address_obj and ipaddress.ip_network(address_obj['ip-netmask'], strict=False).subnet_of(subnet):
            return True
        elif 'fqdn' in address_obj and ipaddress.ip_network(socket.gethostbyname(address_obj["fqdn"]), strict=False).subnet_of(subnet):
            return True
    except (socket.gaierror, TypeError):
        pass
    return False

hosts = ['192.168.10.15/32', '192.168.20.0/24'] # Please add the required subnet/host (use '/32' for host)

pan_object = PaloAltoAPI('https://my-panorama.company.local', os.environ.get('username'), os.environ.get('password'))
addresses = pan_object.get_resource("Objects/Addresses", 'shared')
address_groups = pan_object.get_resource("Objects/AddressGroups", 'shared')

objects_to_romove = []
groups_to_remove = []

print('Connected to Panorama')
print('===========================================')

for host in hosts:
    print(f"Searching for {host}\n")
    subnet = ipaddress.ip_network(host)

    # Process Address Objects
    for object in addresses:
        if process_addr_objects(object, subnet):
            objects_to_romove.append(object['@name'])

    # Process Address Groups
    for group in address_groups:
        new_members = copy.deepcopy(group['static']['member'])
        for member in group['static']['member']:
            address_object = next((object for object in addresses if object["@name"] == member), None)
            if address_object:
                if process_addr_objects(address_object, subnet):
                    new_members.remove(member)
                    print(f"Removing {address_object['@name']} from {group['@name']}")
        
        if group['static']['member'] != new_members:
            if not new_members:
                groups_to_remove.append(group['@name'])
                print()
            else:
                group['static']['member'] = new_members
                data = json.dumps(
                    {
                        "entry": group
                    }
                )
                edit_group = pan_object.edit_resource("Objects/AddressGroups", 'shared', data, group['@name'])
                print(f"{edit_group}\n")

    groups_to_remove = list(set(groups_to_remove))            

    # Process Rules
    for dg, rule_base in device_groups.items():
        rules_to_remove = []
        rules = pan_object.get_resource(f"Policies/Security{rule_base}", dg)
        for rule in rules:
            original_rule = copy.deepcopy(rule)
            for list_key in ['source', 'destination']:
                new_members = copy.deepcopy(rule[list_key]['member'])
                for address in rule[list_key]['member']:
                    if address in groups_to_remove:
                        new_members.remove(address)
                        print(f"Removing {address} from {rule['@name']}")
                    elif address == 'any':
                        continue
                    else:
                        valid_ip = is_valid_ip(address)
                        if valid_ip:
                            try:
                                if ipaddress.ip_network(address, strict=False).subnet_of(subnet):
                                    new_members.remove(address)
                                    print(f"Removing {address} from {rule['@name']}")
                            except TypeError:
                                pass
                        else:
                            address_obj = next((object for object in addresses if object["@name"] == address), None)
                            if address_obj:
                                if process_addr_objects(address_obj, subnet):
                                    new_members.remove(address)
                                    objects_to_romove.append(address)
                                    print(f"Removing {address} from {rule['@name']}")

                if new_members:
                    rule[list_key]['member'] = new_members
                else:
                    rules_to_remove.append(rule['@name'])
                    print()

            if original_rule != rule:
                data = json.dumps(
                    {
                        "entry": rule
                    }
                )
                edit_rules = pan_object.edit_resource(f"Policies/Security{rule_base}", dg, data, rule['@name'])
                print(f"{edit_rules}\n")

        # Remove Empty Rules
        for rule in rules_to_remove:
            print(f"Deleting empty rule - {rule}")
            delete_rules = pan_object.delete_resource(f"Policies/Security{rule_base}", dg, rule)
            print(f"{delete_rules}\n")

print(f"Objects to Remove - {list(set(objects_to_romove))}")
print(f"Groups to remove - {groups_to_remove}")
print()

# Check for Nested Groups
if groups_to_remove:
    for group in address_groups:
        new_members = copy.deepcopy(group['static']['member'])
        for member in group['static']['member']:
            if member in groups_to_remove:
                print(f"Removing {member} from {group['@name']} ")
                new_members.remove(member)
        if group['static']['member'] != new_members:
            group['static']['member'] = new_members
            data = json.dumps(
                {
                    "entry": group
                }
            )
            edit_group = pan_object.edit_resource("Objects/AddressGroups", 'shared', data, group['@name'])
            print(f"{edit_group}\n")

# Remove Empty Groups
for group in groups_to_remove:
    print(f"Deleting Group - {group}")
    delete_groups = pan_object.delete_resource("Objects/AddressGroups", 'shared', group)
    print(delete_groups)
    print()

# Remove Objects
for object in list(set(objects_to_romove)):
    print(f"Deleting Object - {object}")
    delete_objects = pan_object.delete_resource("Objects/Addresses", 'shared', object)
    print(delete_objects)
    print()
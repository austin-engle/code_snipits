"""
For a project I was tasked with taking some json input (data.json) and coverting it to a structured yaml file.
"""

import json
import yaml

def parse_allowed_values(allowed):
    if allowed == "":
        return None
    
    list = allowed.split(',')

    new_list = []
    # Clean data
    for item in list:
        data = item.strip().replace("'",'').replace("[", "").replace("]", '')
        new_list.append(data)
    # Structure data
    values = []

    tcp_ports = {
                "protocol": "tcp",
                "ports": []
                }
    udp_ports = {
                "protocol": "upd",
                "ports": []
                }
    icmp = {
            "protocol": "icmp",
            "ports": []
            }
    icmp_used = False

    for item in new_list:
        if item == 'icmp':
            icmp_used = True
        else:
            data = item.split(':')

            protocol = data[0]
            
            try:
                port = data[1]
                if protocol == 'tcp':
                    tcp_ports['ports'].append(port)
                elif protocol == 'udp':
                    udp_ports['ports'].append(port)
            except:
                pass

    if tcp_ports['ports'] != []:
        values.append(tcp_ports)
    if udp_ports['ports'] != []:
        values.append(udp_ports)
    if icmp_used != False:
        values.append(icmp)

    return values

def main():
    with open('data.json', 'r') as file:
        data = json.load(file)

    output = []

    for item in data:
        
        target_tags = item['targetTags'].split(',')

        source_Ranges = item['sourceRanges'].split(',')

        source_Tags = item['sourceTags'].split(',')

        destination_Ranges = item['destinationRanges']

        if destination_Ranges == "":
            destination_Ranges = None
        else:
            destination_Ranges = destination_Ranges.split(',')

        allowed_data = parse_allowed_values(item['allowed'])


        structured_data = {
                "vpcs": {
                item['name']: {
                    "firewallRules": {
                        item["Networks"]: {
                        "priority": item['priority'],
                        "direction": item['direction'],
                        "description": "",
                        "disabled": item['disabled'],
                        "logging": False,
                        "rule": {
                            "destinationRanges": destination_Ranges,
                            "targetServiceAccounts": None,
                            "targetTags": target_tags,
                            "sourceRanges": source_Ranges,
                            "sourceServiceAccounts": None,
                            "sourceTags": source_Tags,
                            "allow": allowed_data
                        }
                        }
                    }
                }
            }
        }



        # Run for json output
        # data = json.dumps(structured_data)
        # Run for yaml output
        data = yaml.dump(structured_data, allow_unicode=True)
        
        # print(data)
        filename = f'yaml_output/{item["name"]}.yaml'
        with open(filename, 'w') as file:
            file.write(data)


if __name__ == '__main__':
    main()

    # ensure to add '> ouputfile.yml' to end of python run command
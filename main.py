from awsquery import awsquery as q
import csv
import re
import sys
import datetime

today = datetime.date.today()
today_str = today.strftime('%Y-%m-%d')

network_interfaces = q.get_net_interfaces()

for i in range(len(network_interfaces)):
    # EC2s
    if network_interfaces[i]["InterfaceType"] == "interface":
        if network_interfaces[i]["InstanceId"]:
            instance_info = q.get_instance_info(network_interfaces[i]["InstanceId"])
            network_interfaces[i] = network_interfaces[i] | instance_info
        else:
            network_interfaces[i] = network_interfaces[i] | {"Name": network_interfaces[i]["Description"]}
    # VPC Endpoints
    elif network_interfaces[i]["InterfaceType"] in ["vpc_endpoint", "gateway_load_balancer_endpoint"]:
        if "vpce-" in network_interfaces[i]["Description"]:
            start = network_interfaces[i]["Description"].find("vpce-")
            vpc_endpoint_id = network_interfaces[i]["Description"][start : start + 22]
            vpc_endpoint_info = q.get_vpc_endpoint_info(vpc_endpoint_id)
            network_interfaces[i] = network_interfaces[i] | vpc_endpoint_info
    # Lambdas
    elif network_interfaces[i]["InterfaceType"] == "lambda":
        function_name = network_interfaces[i]["Description"][19:-37]
        lambda_info = q.get_lambda_info(function_name)
        network_interfaces[i] = network_interfaces[i] | lambda_info
        network_interfaces[i]["Name"] = function_name
    # Transit Gateways
    elif network_interfaces[i]["InterfaceType"] == "transit_gateway":
        network_interfaces[i] = network_interfaces[i] | {
            "Name": "Transit Gateway Attachment",
            "Project": "SDC-Platform",
        }
    # Network Load Balancer
    elif network_interfaces[i]["InterfaceType"] == "network_load_balancer":
        if "ELB net/" in network_interfaces[i]["Description"]:
            start = network_interfaces[i]["Description"].find("ELB net/") + 8
            load_balancer_name = network_interfaces[i]["Description"][start:]
            load_balancer_info = q.get_net_load_balancer_info(load_balancer_name)
            network_interfaces[i] = network_interfaces[i] | load_balancer_info
    print(network_interfaces[i])
    print("================================================================================")


file_name = "network-interfaces-" + q.get_env() + "_" + today_str + ".csv"
keys = network_interfaces[0].keys()
with open(file_name, "w", newline="") as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(network_interfaces)

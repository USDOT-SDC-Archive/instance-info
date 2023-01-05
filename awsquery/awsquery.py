import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

region_name = "us-east-1"
my_config = Config(
    region_name=region_name,
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"},
)


def get_account_id():
    return boto3.client("sts").get_caller_identity().get("Account")


def get_env():
    session = boto3.Session(region_name=region_name)
    ssm = session.client("ssm")
    ssm_parameter = ssm.get_parameter(Name="environment", WithDecryption=False)
    return ssm_parameter["Parameter"]["Value"]


def get_net_interfaces():
    client = boto3.client("ec2", config=my_config)
    response_iterator = client.get_paginator("describe_network_interfaces").paginate()
    network_interfaces = []
    for page in response_iterator:
        for network_interface in page["NetworkInterfaces"]:
            if "Attachment" in network_interface:
                network_interfaces.append(
                    {
                        "NetworkInterfaceId": network_interface["NetworkInterfaceId"],
                        "InterfaceType": network_interface["InterfaceType"],
                        "PrivateIpAddress": network_interface["PrivateIpAddress"],
                        "InstanceId": network_interface["Attachment"].get("InstanceId", ""),
                        "Description": network_interface["Description"],
                        "Name": "",
                        "Project": "",
                        "Note": "",
                    }
                )
    return network_interfaces


def get_tags(tags):
    name = ""
    project = ""
    if type(tags) == list:
        for tag in tags:
            if tag["Key"] == "Name":
                name = tag["Value"]
            elif tag["Key"] == "Project":
                project = tag["Value"]
    elif type(tags) == dict:
        name = tags.get("Name", "")
        project = tags.get("Project", "")
    return {"Name": name, "Project": project}


def get_instance_info(instance_id):
    client = boto3.client("ec2", config=my_config)
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        tags = response["Reservations"][0]["Instances"][0].get("Tags", [])
        return get_tags(tags)
    except ClientError as e:
        return {"Name": instance_id, "Note": "Unexpected error: %s" % e}


def get_vpc_endpoint_info(vpc_endpoint_id):
    client = boto3.client("ec2", config=my_config)
    try:
        response = client.describe_vpc_endpoints(VpcEndpointIds=[vpc_endpoint_id])
        tags = response["VpcEndpoints"][0].get("Tags", [])
        return get_tags(tags)
    except ClientError as e:
        return {"Name": vpc_endpoint_id, "Note": "Unexpected error: %s" % e}


def get_lambda_info(function_name):
    client = boto3.client("lambda", config=my_config)
    try:
        response = client.get_function(FunctionName=function_name)
        tags = response.get("Tags", [])
        return get_tags(tags)
    except ClientError as e:
        return {"Name": function_name, "Note": "Unexpected error: %s" % e}


def get_net_load_balancer_info(load_balancer_name_id):
    client = boto3.client("elbv2", config=my_config)
    load_balancer_arn = (
        "arn:aws:elasticloadbalancing:"
        + region_name
        + ":"
        + get_account_id()
        + ":loadbalancer/net/"
        + load_balancer_name_id
    )
    try:
        response = client.describe_tags(ResourceArns=[load_balancer_arn])
        tags = response["TagDescriptions"][0].get("Tags", [])
        return get_tags(tags)
    except ClientError as e:
        return {"Name": load_balancer_name_id, "Note": "Unexpected error: %s" % e}

import boto3
import csv
import datetime

today = datetime.date.today()
today_str = today.strftime('%Y-%m-%d')

session = boto3.Session(region_name="us-east-1")

ec2 = session.client("ec2")


def get_env():
    ssm = session.client("ssm")
    ssm_parameter = ssm.get_parameter(Name="environment", WithDecryption=False)
    return ssm_parameter["Parameter"]["Value"]


result = []
response = ec2.describe_instances().get("Reservations")
# print(response)
for item in response:
    for each in item["Instances"]:
        name = ""
        role = ""
        team = ""
        for tag in each["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
            elif tag["Key"] == "Role":
                role = tag["Value"]
            elif tag["Key"] == "Team":
                team = tag["Value"]
        result.append(
            {
                "Name": name,
                "InstanceId": each.get("InstanceId"),
                "PrivateIp": each.get("PrivateIpAddress"),
                "Platform": each.get("Platform"),
                "Role": role,
                "Team": team,
            }
        )

# Sort the list of dict
result = sorted(result, key=lambda d: d["Name"])

# Write to csv file.
file_name = "instance-inventory-" + get_env() + "_" + today_str + ".csv"
header = ["Name", "InstanceId", "PrivateIp", "Platform", "Role", "Team"]
with open(file_name, "w") as file:
    writer = csv.DictWriter(file, fieldnames=header, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result)

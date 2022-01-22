import boto3
import csv

session = boto3.Session(region_name='us-east-1')

ec2 = session.client('ec2')

result = []
# response = ec2.describe_instances(InstanceIds=["i-0cb69169b64fb1843", "i-029550cf92e933e48"]).get('Reservations')
response = ec2.describe_instances().get('Reservations')
# print(response)
for item in response:
    for each in item['Instances']:
        name = ''
        role = ''
        team = ''
        for tag in each['Tags']:
            if tag['Key'] == 'Name':
                name = tag['Value']
            elif tag['Key'] == 'Role':
                role = tag['Value']
            elif tag['Key'] == 'Team':
                team = tag['Value']
        result.append({
            'Name': name,
            'InstanceId': each.get('InstanceId'),
            'PrivateIp': each.get('PrivateIpAddress'),
            'Platform': each.get('Platform'),
            'Role': role,
            'Team': team
        })

# Sort the list of dict
result = sorted(result, key=lambda d: d['Name']) 

# Write to csv file.
header = ['Name', 'InstanceId', 'PrivateIp', 'Platform', 'Role', 'Team']
with open('instance-details.csv', 'w') as file:
    writer = csv.DictWriter(file, fieldnames=header, lineterminator='\n')
    writer.writeheader()
    writer.writerows(result)

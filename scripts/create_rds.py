"""Create a free-tier-friendly MySQL RDS instance with boto3 (alternative to the AWS console).

Usage:  python scripts/create_rds.py --password "StrongPass#123" --region ap-south-1
Needs AWS credentials (`aws configure`) with RDS permissions.
Cost warning: delete the instance when done -> python scripts/delete_rds.py
"""
import argparse

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--identifier", default="cloudbase-db")
ap.add_argument("--password", required=True)
ap.add_argument("--region", default="ap-south-1")
ap.add_argument("--instance-class", default="db.t3.micro")
a = ap.parse_args()

rds = boto3.client("rds", region_name=a.region)
rds.create_db_instance(
    DBInstanceIdentifier=a.identifier,
    DBInstanceClass=a.instance_class,
    Engine="mysql",
    MasterUsername="admin",
    MasterUserPassword=a.password,
    DBName="cloudbase",
    AllocatedStorage=20,
    PubliclyAccessible=True,      # for a demo only; use a private subnet in production
    BackupRetentionPeriod=1,
    StorageEncrypted=True,
)
print("Creating... waiting until available (5-10 minutes)")
rds.get_waiter("db_instance_available").wait(DBInstanceIdentifier=a.identifier)
info = rds.describe_db_instances(DBInstanceIdentifier=a.identifier)["DBInstances"][0]
host = info["Endpoint"]["Address"]
print("Endpoint:", host)
print(f"DATABASE_URL=mysql+pymysql://admin:<password>@{host}:3306/cloudbase")
print("Remember: allow your IP on port 3306 in the instance's security group.")

"""Delete the RDS instance so you are not billed. Usage: python scripts/delete_rds.py"""
import argparse

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--identifier", default="cloudbase-db")
ap.add_argument("--region", default="ap-south-1")
a = ap.parse_args()
boto3.client("rds", region_name=a.region).delete_db_instance(
    DBInstanceIdentifier=a.identifier, SkipFinalSnapshot=True, DeleteAutomatedBackups=True)
print("Deletion started for", a.identifier)

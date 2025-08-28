#!/usr/bin/env python3
"""
Debug script to check AWS credentials and S3 configuration
Run this script to diagnose AWS credential issues
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

def debug_aws_credentials():
    """Debug AWS credentials and S3 configuration"""
    print("=== AWS Credentials Debug ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_bucket_name = os.getenv('S3_BUCKET_NAME')
    
    print(f"AWS_ACCESS_KEY_ID: {'Set' if aws_access_key_id else 'NOT SET'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'Set' if aws_secret_access_key else 'NOT SET'}")
    print(f"AWS_REGION: {aws_region}")
    print(f"S3_BUCKET_NAME: {s3_bucket_name or 'NOT SET'}")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("\n❌ AWS credentials are missing!")
        print("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        return False
    
    if not s3_bucket_name:
        print("\n❌ S3 bucket name is missing!")
        print("Please set S3_BUCKET_NAME environment variable")
        return False
    
    # Test AWS credentials
    try:
        print("\n=== Testing AWS Credentials ===")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        # Test credentials by accessing the specific bucket instead of listing all buckets
        try:
            s3_client.head_bucket(Bucket=s3_bucket_name)
            print("✅ AWS credentials are valid!")
            print(f"✅ Have access to bucket '{s3_bucket_name}'")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{s3_bucket_name}' not found")
            elif error_code == '403':
                print(f"❌ No access to bucket '{s3_bucket_name}'")
            else:
                print(f"❌ Error accessing bucket: {e}")
            return False
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS ClientError: {error_code} - {error_message}")
        
        if error_code == 'SignatureDoesNotMatch':
            print("\n🔍 SignatureDoesNotMatch usually means:")
            print("1. Incorrect AWS Access Key ID")
            print("2. Incorrect AWS Secret Access Key")
            print("3. Wrong AWS Region")
            print("4. Clock synchronization issues")
        elif error_code == 'AccessDenied':
            print("\n🔍 AccessDenied usually means:")
            print("1. Insufficient IAM permissions")
            print("2. Bucket doesn't exist")
            print("3. Wrong bucket name")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = debug_aws_credentials()
    if success:
        print("\n✅ AWS configuration looks good!")
    else:
        print("\n❌ AWS configuration has issues. Please fix them before running the app.")

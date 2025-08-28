import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_s3_client():
    """Get S3 client with credentials from environment variables"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        return s3_client
    except NoCredentialsError:
        print("AWS credentials not found. S3 upload will be skipped.")
        return None

def upload_to_s3(file_path: str, original_filename: str) -> str:
    """Upload file to S3 and return the URL"""
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("S3 bucket name not configured. File upload skipped.")
        return None
    
    try:
        # Generate unique filename to avoid conflicts
        file_extension = original_filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload file
        s3_client.upload_file(
            file_path,
            bucket_name,
            unique_filename,
            ExtraArgs={
                'ContentType': 'application/pdf',
                'ACL': 'private'  # or 'public-read' if you want public access
            }
        )
        
        # Generate URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
        return s3_url
        
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error uploading to S3: {e}")
        return None

def delete_from_s3(s3_url: str) -> bool:
    """Delete file from S3"""
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        return False
    
    try:
        # Extract key from URL
        key = s3_url.split(f"{bucket_name}.s3.amazonaws.com/")[-1]
        
        # Delete file
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )
        return True
        
    except ClientError as e:
        print(f"Error deleting from S3: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error deleting from S3: {e}")
        return False

def get_s3_file_url(s3_url: str) -> str:
    """Generate a presigned URL for private S3 files"""
    s3_client = get_s3_client()
    if not s3_client:
        return s3_url
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        return s3_url
    
    try:
        # Extract key from URL
        key = s3_url.split(f"{bucket_name}.s3.amazonaws.com/")[-1]
        
        # Generate presigned URL (expires in 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=3600
        )
        return presigned_url
        
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return s3_url

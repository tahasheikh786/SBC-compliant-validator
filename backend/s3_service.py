import boto3
import os
import uuid
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

# Get AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

def get_s3_client():
    """Get S3 client with credentials from environment variables"""
    try:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            print("AWS credentials not found in environment variables")
            print(f"AWS_ACCESS_KEY_ID: {'Set' if AWS_ACCESS_KEY_ID else 'Not set'}")
            print(f"AWS_SECRET_ACCESS_KEY: {'Set' if AWS_SECRET_ACCESS_KEY else 'Not set'}")
            print(f"AWS_REGION: {AWS_REGION}")
            return None
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        print("AWS S3 client created successfully")
        return s3_client
        
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

def upload_to_s3(file_path: str, original_filename: str) -> str:
    """Upload file to S3 and return the URL"""
    s3_client = get_s3_client()
    if not s3_client:
        print("S3 client not available. Skipping upload.")
        return None
    
    if not S3_BUCKET_NAME:
        print("S3 bucket name not configured. File upload skipped.")
        return None
    
    try:
        # Generate unique filename to avoid conflicts
        file_extension = original_filename.split('.')[-1]
        unique_filename = f"text-extraction-pdf/{uuid.uuid4()}.{file_extension}"
        
        print(f"Attempting to upload {file_path} to S3 bucket {S3_BUCKET_NAME} as {unique_filename}")
        print(f"Using region: {AWS_REGION}")
        print(f"AWS credentials available: {bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)}")
        
        # Upload file using the same pattern as your working code
        s3_client.upload_file(
            file_path,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': 'application/pdf',
                'ContentDisposition': 'inline'
            }
        )
        
        print(f"Successfully uploaded to S3: {unique_filename}")
        
        # Generate URL using the same pattern as your working code
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return s3_url
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"S3 ClientError: {error_code} - {error_message}")
        
        if error_code == 'SignatureDoesNotMatch':
            print("This usually indicates incorrect AWS credentials or region mismatch")
            print("Please check your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION")
        
        return None
    except Exception as e:
        print(f"Unexpected error uploading to S3: {e}")
        return None

def delete_from_s3(s3_url: str) -> bool:
    """Delete file from S3"""
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    if not S3_BUCKET_NAME:
        return False
    
    try:
        # Extract key from URL
        key = s3_url.split(f"{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/")[-1]
        
        # Delete file
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )
        print(f"Successfully deleted from S3: {key}")
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
    
    if not S3_BUCKET_NAME:
        return s3_url
    
    try:
        # Extract key from URL
        key = s3_url.split(f"{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/")[-1]
        
        # Generate presigned URL using the same pattern as your working code
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': key,
                'ResponseContentDisposition': 'inline'
            },
            ExpiresIn=3600
        )
        return presigned_url
        
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return s3_url

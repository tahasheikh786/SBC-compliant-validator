import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
from dotenv import load_dotenv
from database import init_db, insert_record, get_all_records
from pdf_processor import process_sbc_pdf
from s3_service import upload_to_s3, delete_from_s3

# Load environment variables
load_dotenv()

app = FastAPI(title="SBC Document Processor API")

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://sbc-compliant-validator.vercel.app').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add explicit OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SBC Compliant Validator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "records": "/api/records",
            "upload": "/api/upload",
            "delete_record": "/api/records/{record_id}"
        },
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "SBC Processor API is running"}

@app.get("/api/records")
async def get_records():
    """Get all processed SBC records"""
    try:
        records = get_all_records()
        return {
            'success': True,
            'records': records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Process uploaded SBC file with intelligent explanations"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the PDF with enhanced explanations
            result = process_sbc_pdf(temp_file_path)
            
            if result['success']:
                # Upload to S3
                s3_url = upload_to_s3(temp_file_path, file.filename)
                
                # If S3 upload fails, still save the record but without S3 URL
                if s3_url is None:
                    print("Warning: S3 upload failed, saving record without S3 URL")
                    s3_url = None
                
                # Insert into database with explanations
                insert_record(
                    result['company_name'],
                    result['penalty_a'],
                    result['penalty_b'],
                    file.filename,
                    s3_url,
                    result.get('penalty_a_explanation'),  # NEW
                    result.get('penalty_b_explanation')   # NEW
                )
                
                response_data = {
                    'success': True,
                    'message': 'File processed successfully!',
                    'data': {
                        'company_name': result['company_name'],
                        'penalty_a': result['penalty_a'],
                        'penalty_b': result['penalty_b'],
                        'penalty_a_explanation': result.get('penalty_a_explanation', ''),  # NEW
                        'penalty_b_explanation': result.get('penalty_b_explanation', ''), # NEW
                        'filename': file.filename
                    }
                }
                
                if s3_url is None:
                    response_data['warning'] = 'File processed but S3 upload failed. Data saved locally.'
                
                return response_data
            else:
                raise HTTPException(status_code=400, detail=f"Error processing file: {result['error']}")
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in upload endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int):
    """Delete a record and its associated S3 file"""
    try:
        from database import delete_record as db_delete_record, get_record_by_id
        
        # Get the record first to get the S3 URL
        record = get_record_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Delete from S3 if URL exists
        if record.get('s3_url'):
            try:
                delete_from_s3(record['s3_url'])
            except Exception as s3_error:
                print(f"Warning: Failed to delete S3 file: {s3_error}")
        
        # Delete the record from database
        db_delete_record(record_id)
        
        return {
            'success': True,
            'message': 'Record deleted successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Initialize database
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=5000)

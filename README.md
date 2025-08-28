# SBC Document Processor

A full-stack web application for processing Summary of Benefits and Coverage (SBC) PDF documents. The application extracts specific information from SBC documents and displays the results in a modern, user-friendly interface.

## Features

- **PDF Processing**: Extract company names and coverage information from SBC documents
- **Smart Analysis**: Automatically determine penalties based on coverage answers
- **Modern UI**: React frontend with Material-UI components
- **Cloud Storage**: AWS S3 integration for file storage
- **Database**: PostgreSQL database for data persistence
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- **Flask**: Python web framework
- **pdfplumber**: PDF text extraction
- **PostgreSQL**: Database (via Render)
- **AWS S3**: File storage
- **Gunicorn**: Production WSGI server

### Frontend
- **React**: JavaScript framework
- **Material-UI**: UI component library
- **React Dropzone**: File upload component
- **Axios**: HTTP client

## Project Structure

```
sbc-processor/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database operations
│   ├── pdf_processor.py    # PDF processing logic
│   ├── s3_service.py       # AWS S3 integration
│   └── gunicorn.conf.py    # Production server config
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── public/             # Static files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account (for S3)
- Render Account (for database and hosting)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sbc-processor
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration (Render PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database_name

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_s3_bucket_name

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-change-this
FLASK_ENV=development

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### 5. Database Setup

1. Create a PostgreSQL database on Render
2. Update the `DATABASE_URL` in your `.env` file
3. The application will automatically create the required tables

### 6. AWS S3 Setup

1. Create an S3 bucket in your AWS account
2. Create an IAM user with S3 access
3. Update the AWS credentials in your `.env` file

## Running the Application

### Development Mode

1. **Start the Backend**:
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm start
   ```
   The frontend will run on `http://localhost:3000`

### Production Deployment

#### Backend Deployment (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following environment variables:
   - `DATABASE_URL`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `S3_BUCKET_NAME`
   - `FLASK_SECRET_KEY`
   - `CORS_ORIGINS`

4. Set the build command:
   ```bash
   pip install -r requirements.txt
   ```

5. Set the start command:
   ```bash
   gunicorn app:app
   ```

#### Frontend Deployment

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy the `build` folder to your preferred hosting service (Netlify, Vercel, etc.)

3. Update the `REACT_APP_API_URL` environment variable to point to your backend URL

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/records` - Get all processed records
- `POST /api/upload` - Upload and process SBC file
- `DELETE /api/records/<id>` - Delete a record

## Usage

1. **Upload SBC Document**: Navigate to the Upload page and drag & drop a PDF file
2. **View Results**: Check the Dashboard to see all processed documents
3. **Analyze Data**: View statistics and penalty information for each document

## PDF Processing Logic

The application extracts the following information from SBC documents:

1. **Company Name**: Extracted from the first page using pattern matching
2. **Minimum Essential Coverage**: Searches for "Yes/No" answers
3. **Minimum Value Standards**: Searches for "Yes/No" answers
4. **Penalty Calculation**: 
   - Penalty A: "No" if Essential Coverage is "Yes", otherwise "Yes"
   - Penalty B: "No" if Value Standards is "Yes", otherwise "Yes"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the GitHub repository.

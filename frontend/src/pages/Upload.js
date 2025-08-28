import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Button,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  ArrowBack as ArrowBackIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { uploadFile } from '../services/api';
import ExplanationTooltip from '../components/ExplanationTooltip';

const Upload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    // Validate file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
      setError('File size must be less than 16MB');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setUploadResult(null);

      const response = await uploadFile(file);
      
      if (response.success) {
        setUploadResult(response.data);
        // Automatically redirect to dashboard after successful upload
        setTimeout(() => {
          navigate('/');
        }, 5000); // Wait 5 seconds to show success message and explanations
      } else {
        setError(response.error || 'Failed to process file');
      }
    } catch (err) {
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: uploading
  });

  const handleViewResults = () => {
    navigate('/');
  };

  const getPenaltyColor = (penalty) => {
    if (penalty === 'Yes') return 'success';
    if (penalty === 'No') return 'error';
    return 'warning';
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mr: 2 }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h4" component="h1">
          Upload SBC Document
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {uploadResult && (
        <Alert severity="success" sx={{ mb: 3 }}>
          File processed successfully! Company: {uploadResult.company_name}. Redirecting to dashboard in 5 seconds...
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper
            {...getRootProps()}
            sx={{
              p: 4,
              textAlign: 'center',
              cursor: uploading ? 'not-allowed' : 'pointer',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'action.hover',
              },
            }}
          >
            <input {...getInputProps()} />
            
            {uploading ? (
              <Box>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Processing SBC Document...
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Please wait while we extract information and generate smart explanations from your PDF
                </Typography>
              </Box>
            ) : (
              <Box>
                <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF file here'}
                </Typography>
                <Typography variant="body1" color="textSecondary" gutterBottom>
                  or click to select a file
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Maximum file size: 16MB
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                What this processor does:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Extracts company name from the SBC document" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Finds answers to 'Minimum Essential Coverage' question" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Finds answers to 'Minimum Value Standards' question" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Generates intelligent compliance explanations" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Calculates penalties based on the answers" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary="Stores results in a table for easy viewing" />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          {uploadResult && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Results:
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Company:</strong> {uploadResult.company_name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      label={`Essential Coverage: ${uploadResult.penalty_a}`}
                      color={getPenaltyColor(uploadResult.penalty_a)}
                      size="small"
                    />
                    <Chip
                      label={`Value Standards: ${uploadResult.penalty_b}`}
                      color={getPenaltyColor(uploadResult.penalty_b)}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2">
                    <strong>Filename:</strong> {uploadResult.filename}
                  </Typography>
                </Box>

                {/* Smart Explanations */}
                {(uploadResult.penalty_a_explanation || uploadResult.penalty_b_explanation) && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      Smart Analysis:
                    </Typography>
                    
                    {uploadResult.penalty_a_explanation && (
                      <Accordion sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <InfoIcon fontSize="small" color="primary" />
                            <Typography variant="body2">
                              Essential Coverage Analysis
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              whiteSpace: 'pre-line',
                              fontSize: '0.75rem',
                              color: 'text.secondary'
                            }}
                          >
                            {uploadResult.penalty_a_explanation}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    )}

                    {uploadResult.penalty_b_explanation && (
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <InfoIcon fontSize="small" color="primary" />
                            <Typography variant="body2">
                              Value Standards Analysis
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              whiteSpace: 'pre-line',
                              fontSize: '0.75rem',
                              color: 'text.secondary'
                            }}
                          >
                            {uploadResult.penalty_b_explanation}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    )}
                  </Box>
                )}

                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleViewResults}
                  sx={{ mt: 2 }}
                >
                  View All Results
                </Button>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Upload;

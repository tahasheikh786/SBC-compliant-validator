import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Button,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getRecords, deleteRecord } from '../services/api';

const Dashboard = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchRecords = async () => {
    try {
      setLoading(true);
      const response = await getRecords();
      if (response.success) {
        setRecords(response.records);
      } else {
        setError(response.error || 'Failed to fetch records');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleDelete = async (recordId) => {
    try {
      const response = await deleteRecord(recordId);
      if (response.success) {
        setRecords(records.filter(record => record.id !== recordId));
      } else {
        setError(response.error || 'Failed to delete record');
      }
    } catch (err) {
      setError('Failed to delete record');
    }
  };

  const getPenaltyColor = (penalty) => {
    // For direct answers: "Yes" is good (green), "No" is bad (red), "Unknown" is warning (orange)
    if (penalty === 'Yes') return 'success';
    if (penalty === 'No') return 'error';
    return 'warning';
  };

  const getStatistics = () => {
    const totalRecords = records.length;
    const penaltyARecords = records.filter(r => r.penalty_a === 'No').length; // Count "No" answers as penalties
    const penaltyBRecords = records.filter(r => r.penalty_b === 'No').length; // Count "No" answers as penalties
    
    return { totalRecords, penaltyARecords, penaltyBRecords };
  };

  const stats = getStatistics();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          SBC Records Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchRecords}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => navigate('/upload')}
          >
            Upload New File
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Records
              </Typography>
              <Typography variant="h4">
                {stats.totalRecords}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Essential Coverage (No)
              </Typography>
              <Typography variant="h4" color="error">
                {stats.penaltyARecords}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Value Standards (No)
              </Typography>
              <Typography variant="h4" color="error">
                {stats.penaltyBRecords}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Records Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Group (Company Name)</TableCell>
                <TableCell>Date of Upload</TableCell>
                <TableCell>Essential Coverage</TableCell>
                <TableCell>Value Standards</TableCell>
                <TableCell>Filename</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {records.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body1" color="textSecondary" sx={{ py: 4 }}>
                      No SBC files have been processed yet.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                records.map((record) => (
                  <TableRow key={record.id} hover>
                    <TableCell>{record.group_name}</TableCell>
                    <TableCell>{record.upload_date}</TableCell>
                    <TableCell>
                      <Chip
                        label={record.penalty_a}
                        color={getPenaltyColor(record.penalty_a)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={record.penalty_b}
                        color={getPenaltyColor(record.penalty_b)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{record.filename}</TableCell>
                    <TableCell>
                      <IconButton
                        color="error"
                        onClick={() => handleDelete(record.id)}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Dashboard;

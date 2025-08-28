import React from 'react';
import {
  Tooltip,
  Box,
  Typography,
  Divider,
  Chip,
  Paper,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const ExplanationTooltip = ({ 
  children, 
  penaltyAExplanation, 
  penaltyBExplanation, 
  penaltyA, 
  penaltyB,
  companyName 
}) => {
  // Debug logging
  console.log('ExplanationTooltip props:', {
    companyName,
    penaltyA,
    penaltyB,
    penaltyAExplanation: penaltyAExplanation ? penaltyAExplanation.substring(0, 50) + '...' : 'null',
    penaltyBExplanation: penaltyBExplanation ? penaltyBExplanation.substring(0, 50) + '...' : 'null'
  });

  const formatExplanation = (explanation) => {
    if (!explanation) return '';
    
    // Split by bullet points and format
    const sections = explanation.split('\n\n');
    return sections.map((section, index) => {
      const lines = section.split('\n');
      const title = lines[0];
      const content = lines.slice(1);
      
      return (
        <Box key={index} sx={{ mb: 2 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              fontWeight: 'bold', 
              mb: 1,
              color: title.includes('✅') ? 'success.main' : 
                     title.includes('❌') ? 'error.main' : 'primary.main'
            }}
          >
            {title}
          </Typography>
          {content.map((line, lineIndex) => {
            if (line.trim().startsWith('•')) {
              return (
                <Typography 
                  key={lineIndex} 
                  variant="body2" 
                  sx={{ 
                    ml: 1, 
                    mb: 0.5,
                    color: 'text.secondary',
                    fontSize: '0.75rem'
                  }}
                >
                  {line}
                </Typography>
              );
            } else if (line.trim()) {
              return (
                <Typography 
                  key={lineIndex} 
                  variant="body2" 
                  sx={{ 
                    mb: 0.5,
                    color: 'text.secondary',
                    fontSize: '0.75rem'
                  }}
                >
                  {line}
                </Typography>
              );
            }
            return null;
          })}
        </Box>
      );
    });
  };

  const tooltipContent = (
    <Paper 
      elevation={8} 
      sx={{ 
        p: 2, 
        maxWidth: 500, 
        backgroundColor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 'bold',
            color: 'primary.main',
            mb: 1
          }}
        >
          {companyName}
        </Typography>
        <Divider sx={{ mb: 2 }} />
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip
          icon={penaltyA === 'Yes' ? <CheckIcon /> : <CancelIcon />}
          label={`Essential Coverage: ${penaltyA}`}
          color={penaltyA === 'Yes' ? 'success' : penaltyA === 'No' ? 'error' : 'warning'}
          size="small"
          variant="outlined"
        />
        <Chip
          icon={penaltyB === 'Yes' ? <CheckIcon /> : <CancelIcon />}
          label={`Value Standards: ${penaltyB}`}
          color={penaltyB === 'Yes' ? 'success' : penaltyB === 'No' ? 'error' : 'warning'}
          size="small"
          variant="outlined"
        />
      </Box>

      <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
        {penaltyAExplanation && (
          <Box sx={{ mb: 3 }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                fontWeight: 'bold', 
                mb: 1,
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}
            >
              <InfoIcon fontSize="small" />
              Minimum Essential Coverage Analysis
            </Typography>
            {formatExplanation(penaltyAExplanation)}
          </Box>
        )}

        {penaltyBExplanation && (
          <Box>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                fontWeight: 'bold', 
                mb: 1,
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                gap: 0.5
              }}
            >
              <InfoIcon fontSize="small" />
              Minimum Value Standards Analysis
            </Typography>
            {formatExplanation(penaltyBExplanation)}
          </Box>
        )}

        {!penaltyAExplanation && !penaltyBExplanation && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body2" color="text.secondary">
              No explanations available for this record.
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );

  return (
    <Tooltip
      title={tooltipContent}
      placement="top-start"
      arrow
      PopperProps={{
        sx: {
          '& .MuiTooltip-tooltip': {
            backgroundColor: 'transparent',
            boxShadow: 'none',
            p: 0,
            maxWidth: 'none',
          },
        },
      }}
    >
      {children}
    </Tooltip>
  );
};

export default ExplanationTooltip;

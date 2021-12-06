/* eslint-disable @typescript-eslint/no-explicit-any*/
import React from 'react';
import {useGlobalContext} from './GlobalContext';
import { Box, createTheme, ThemeProvider } from '@mui/system';
import { Paper } from '@mui/material';

const theme = createTheme({
    palette: {
      background: {
        paper: '#fff',
      },
      text: {
        primary: '#173A5E',
        secondary: '#46505A',
      },
      action: {
        active: '#001E3C',
      },
      success: {
        dark: '#009688',
      },
    },
  });
  
export const Overview = () : JSX.Element => {

    const {testResult} = useGlobalContext();

    return (
        <div>
            <Paper elevation={5}>
            <ThemeProvider theme={theme}>
            <Box component="div"
        sx={{
          bgcolor: 'background.paper',
          boxShadow: 1,
          borderRadius: 1,
          p: 2,
          minWidth: 300,
          display: 'inline-flex',
          flexDirection: 'row'
        }}
      >
        <Box sx={{ color: 'text.secondary' }}>Elapsed<Box sx={{ color: 'text.primary', fontSize: 20, fontWeight: 'medium', display: 'block' }}>
          {testResult.elapsed.toFixed(2)} (s)
        </Box></Box>
      </Box>
      <Box component="div"
        sx={{
          bgcolor: 'background.paper',
          boxShadow: 1,
          borderRadius: 1,
          p: 2,
          minWidth: 300,
          display: 'inline-flex',
          flexDirection: 'row'
        }}
      >
        <Box sx={{ color: 'text.secondary' }}>CPU Cores<Box sx={{ color: 'text.primary', fontSize: 20, fontWeight: 'medium', display: 'block' }}>
          {testResult.numCpu}
        </Box></Box>
      </Box>
      <Box component="div"
        sx={{
          bgcolor: 'background.paper',
          boxShadow: 1,
          borderRadius: 1,
          p: 2,
          minWidth: 300,
          display: 'inline-flex',
          flexDirection: 'row'
        }}
      >
        <Box sx={{ color: 'text.secondary' }}>Start<Box sx={{ color: 'text.primary', fontSize: 20, fontWeight: 'medium', display: 'block' }}>
          {testResult.start}
        </Box></Box>
      </Box>
      <Box component="div"
        sx={{
          bgcolor: 'background.paper',
          boxShadow: 1,
          borderRadius: 1,
          p: 2,
          minWidth: 300,
          display: 'inline-flex',
          flexDirection: 'row'
        }}
      >
        <Box sx={{ color: 'text.secondary' }}>End<Box sx={{ color: 'text.primary', fontSize: 20, fontWeight: 'medium', display: 'block' }}>
          {testResult.end}
        </Box></Box>
      </Box>
      </ThemeProvider>
      </Paper>
        </div>
    )
}
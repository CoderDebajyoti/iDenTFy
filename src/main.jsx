import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { VerificationProvider } from './context/VerificationContext';

// Global Vanilla CSS System
import './styles/index.css';
import './styles/layout.css';
import './styles/components.css';
import './styles/pages.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <VerificationProvider>
        <App />
      </VerificationProvider>
    </BrowserRouter>
  </React.StrictMode>
);

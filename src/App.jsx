import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';

// Pages
import Home from './pages/Home';
import DocumentVerification from './pages/DocumentVerification';
import DocumentProcessing from './pages/DocumentProcessing';
import DocumentResult from './pages/DocumentResult';
import FaceVerification from './pages/FaceVerification';
import FinalResult from './pages/FinalResult';
import History from './pages/History';
import VerificationDetails from './pages/VerificationDetails';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/verify" element={<Navigate to="/verify/document" replace />} />
        <Route path="/verify/document" element={<DocumentVerification />} />
        <Route path="/verify/document/processing" element={<DocumentProcessing />} />
        <Route path="/verify/document/result" element={<DocumentResult />} />
        <Route path="/verify/face" element={<FaceVerification />} />
        <Route path="/verify/final" element={<FinalResult />} />
        <Route path="/history" element={<History />} />
        <Route path="/history/:id" element={<VerificationDetails />} />
        <Route path="/settings" element={<Settings />} />
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

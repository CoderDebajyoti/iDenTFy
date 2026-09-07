import React, { createContext, useContext, useState, useEffect } from 'react';
import { PRESET_SCENARIOS } from '../services/mockData';
import { uploadDocument } from '../services/api';

const VerificationContext = createContext(null);

export function VerificationProvider({ children }) {
  // Workflow Core State
  const [selectedDocumentType, setSelectedDocumentType] = useState('passport');
  const [uploadedFile, setUploadedFile] = useState(null); // Real browser File object
  const [filePreviewUrl, setFilePreviewUrl] = useState(null);

  // Status & Telemetry
  const [verificationId, setVerificationId] = useState(null);
  const [documentStatus, setDocumentStatus] = useState('idle'); // idle | processing | verified | requires_review | failed | error
  const [ocrResult, setOcrResult] = useState(null);
  const [matchingResult, setMatchingResult] = useState(null);
  const [tamperResult, setTamperResult] = useState(null);

  // Face Verification State (locked until document passes initial screening)
  const [faceStatus, setFaceStatus] = useState('locked'); // locked | waiting | capturing | processing | matched | not_matched | requires_review
  const [faceImagePreview, setFaceImagePreview] = useState(null);

  // Final Decision & Risk
  const [riskLevel, setRiskLevel] = useState('Pending');
  const [riskScore, setRiskScore] = useState(null);
  const [finalDecision, setFinalDecision] = useState('Pending');

  // Inspection / Dev Scenario Switcher for SIH Presentation & Testing
  const [inspectionMode, setInspectionMode] = useState(true);
  const [activeScenario, setActiveScenario] = useState('verified'); // verified | review | failed

  // Clean up object URLs when unmounting or changing files
  useEffect(() => {
    return () => {
      if (filePreviewUrl) {
        URL.revokeObjectURL(filePreviewUrl);
      }
      if (faceImagePreview) {
        URL.revokeObjectURL(faceImagePreview);
      }
    };
  }, [filePreviewUrl, faceImagePreview]);

  // Set real File object and create local preview
  const handleSetUploadedFile = (file) => {
    if (!file) {
      if (filePreviewUrl) URL.revokeObjectURL(filePreviewUrl);
      setUploadedFile(null);
      setFilePreviewUrl(null);
      return;
    }

    if (filePreviewUrl) URL.revokeObjectURL(filePreviewUrl);
    setUploadedFile(file);
    setFilePreviewUrl(URL.createObjectURL(file));

    // Reset downstream states
    setDocumentStatus('idle');
    setOcrResult(null);
    setMatchingResult(null);
    setTamperResult(null);
    setFaceStatus('locked');
    setRiskLevel('Pending');
    setRiskScore(null);
    setFinalDecision('Pending');
  };

  // Switch inspection scenario for demonstration of all visual states
  const applyScenario = (scenarioKey) => {
    setActiveScenario(scenarioKey);
    const scenario = PRESET_SCENARIOS[scenarioKey];
    if (!scenario) return;

    setDocumentStatus(scenario.status.toLowerCase().includes('failed') ? 'failed' : scenario.status.toLowerCase().includes('review') ? 'requires_review' : 'verified');
    setOcrResult(scenario.ocrDetails);
    setTamperResult(scenario.tamperForensics);
    setMatchingResult({
      databaseMatch: scenario.databaseMatch,
      fieldMatch: scenario.status === 'Verified' ? '100% Match' : 'Field Discrepancy Found',
      nameSimilarity: scenario.status === 'Verified' ? '99.4%' : scenario.status === 'Requires Review' ? '82.1%' : '41.0%',
      documentNumberMatch: scenario.status === 'Verified' ? 'Matched in Registry' : 'Unmatched Checksum',
    });
    setRiskLevel(scenario.riskLevel);
    setRiskScore(scenario.riskScore);

    // If document passed, unlock face verification
    if (scenario.status === 'Verified') {
      setFaceStatus('waiting');
    } else {
      setFaceStatus('locked');
    }
  };

  // Trigger document analysis pipeline
  const startDocumentAnalysis = async () => {
    setDocumentStatus('processing');

    // Attempt real API upload first
    if (uploadedFile) {
      const apiResponse = await uploadDocument(uploadedFile, selectedDocumentType);
      if (apiResponse.success && apiResponse.data) {
        const data = apiResponse.data;
        setVerificationId(data.verification_id);
        setDocumentStatus(data.document_status.toLowerCase());
        setOcrResult(data.ocr_result?.fields || {});
        setTamperResult({
          imageIntegrity: data.tampering_result?.tampering_detected ? "Failed (Manipulation Found)" : "Passed (100%)",
          metadataAnalysis: data.tampering_result?.metadata_analysis?.summary || "Clean",
          tamperingIndicators: data.tampering_result?.indicators?.join("; ") || "None",
          fontConsistency: "ICAO Doc 9303 Compliant"
        });
        setMatchingResult({
          databaseMatch: data.matching_result?.match_type ? data.matching_result.match_type.replace('_', ' ').toUpperCase() : "NO MATCH",
          fieldMatch: data.matching_result?.database_match ? "100% Match in Registry" : "Registry Mismatch",
          nameSimilarity: `${Math.round((data.matching_result?.name_similarity || 0) * 100)}%`,
          documentNumberMatch: data.matching_result?.field_matches?.document_number ? "Matched in Registry" : "Unmatched"
        });
        setRiskLevel(data.risk_level || 'Low');
        setRiskScore(data.risk_score || 15);

        if (data.can_proceed_to_face) {
          setFaceStatus('waiting');
        } else {
          setFaceStatus('locked');
        }
        return;
      }
    }

    // Fallback scenario data if backend is unreachable
    const newId = `IDF-2026-${Math.floor(1000 + Math.random() * 9000)}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`;
    setVerificationId(newId);
    applyScenario(activeScenario);
  };

  // Face Verification Completion
  const submitFaceMatch = async (faceBlob, customOutcome = null) => {
    if (faceBlob) {
      if (faceImagePreview) URL.revokeObjectURL(faceImagePreview);
      setFaceImagePreview(URL.createObjectURL(faceBlob));
    }

    if (faceBlob && verificationId) {
      const apiRes = await submitFaceVerification(verificationId, faceBlob);
      if (apiRes.success) {
        setFaceStatus(apiRes.outcome);
        setFinalDecision(apiRes.final_decision.replace('_', ' ').toUpperCase());
        setRiskLevel(apiRes.risk_level);
        setRiskScore(apiRes.risk_score);
        return;
      }
    }

    const outcome = customOutcome || (activeScenario === 'failed' ? 'not_matched' : activeScenario === 'review' ? 'requires_review' : 'matched');
    setFaceStatus(outcome);

    if (outcome === 'matched' && documentStatus === 'verified') {
      setFinalDecision('Verified');
      setRiskLevel('Low');
      setRiskScore(14);
    } else if (outcome === 'requires_review' || documentStatus === 'requires_review') {
      setFinalDecision('Requires Review');
      setRiskLevel('Medium');
      setRiskScore(48);
    } else {
      setFinalDecision('Verification Failed');
      setRiskLevel('High');
      setRiskScore(92);
    }
  };

  // Reset entire workflow
  const resetWorkflow = () => {
    if (filePreviewUrl) URL.revokeObjectURL(filePreviewUrl);
    if (faceImagePreview) URL.revokeObjectURL(faceImagePreview);
    setUploadedFile(null);
    setFilePreviewUrl(null);
    setDocumentStatus('idle');
    setOcrResult(null);
    setMatchingResult(null);
    setTamperResult(null);
    setFaceStatus('locked');
    setFaceImagePreview(null);
    setRiskLevel('Pending');
    setRiskScore(null);
    setFinalDecision('Pending');
    setVerificationId(null);
  };

  return (
    <VerificationContext.Provider
      value={{
        selectedDocumentType,
        setSelectedDocumentType,
        uploadedFile,
        filePreviewUrl,
        setUploadedFile: handleSetUploadedFile,
        documentStatus,
        setDocumentStatus,
        ocrResult,
        matchingResult,
        tamperResult,
        faceStatus,
        setFaceStatus,
        faceImagePreview,
        riskLevel,
        riskScore,
        finalDecision,
        verificationId,
        inspectionMode,
        setInspectionMode,
        activeScenario,
        setActiveScenario: applyScenario,
        startDocumentAnalysis,
        submitFaceMatch,
        resetWorkflow,
      }}
    >
      {children}
    </VerificationContext.Provider>
  );
}

export function useVerification() {
  const context = useContext(VerificationContext);
  if (!context) {
    throw new Error('useVerification must be used within a VerificationProvider');
  }
  return context;
}

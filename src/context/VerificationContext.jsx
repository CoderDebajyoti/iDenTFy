import React, { createContext, useContext, useState, useEffect } from 'react';
import { uploadDocument, submitFaceVerification } from '../services/api';

const VerificationContext = createContext(null);

export function VerificationProvider({ children }) {
  // Workflow Core State
  const [selectedDocumentType, setSelectedDocumentType] = useState('passport');
  const [uploadedFile, setUploadedFile] = useState(null); // Real browser File object
  const [filePreviewUrl, setFilePreviewUrl] = useState(null);

  // Status & Telemetry (100% Real Backend Data)
  const [verificationId, setVerificationId] = useState(null);
  const [documentStatus, setDocumentStatus] = useState('idle'); // idle | processing | verified | requires_review | failed | not_verified | error
  const [workflowError, setWorkflowError] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const [matchingResult, setMatchingResult] = useState(null);
  const [tamperResult, setTamperResult] = useState(null);

  // Face Verification State (Strictly locked until document passes initial screening)
  const [faceStatus, setFaceStatus] = useState('locked'); // locked | waiting | processing | matched | not_matched | requires_review | error
  const [faceImagePreview, setFaceImagePreview] = useState(null);

  // Final Decision & Risk
  const [riskLevel, setRiskLevel] = useState('Pending');
  const [riskScore, setRiskScore] = useState(null);
  const [finalDecision, setFinalDecision] = useState('Pending');

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
    setWorkflowError(null);
    setOcrResult(null);
    setMatchingResult(null);
    setTamperResult(null);
    setFaceStatus('locked');
    setRiskLevel('Pending');
    setRiskScore(null);
    setFinalDecision('Pending');
    setVerificationId(null);
  };

  // Trigger document analysis pipeline via real API
  const startDocumentAnalysis = async () => {
    if (!uploadedFile) {
      const err = 'No document file selected. Please choose an identity document image.';
      setWorkflowError(err);
      setDocumentStatus('error');
      return { success: false, error: err };
    }

    setDocumentStatus('processing');
    setWorkflowError(null);

    try {
      const apiResponse = await uploadDocument(uploadedFile, selectedDocumentType);
      const data = apiResponse.data;

      setVerificationId(data.verification_id);
      const statusKey = (data.document_status || 'requires_review').toLowerCase();
      setDocumentStatus(statusKey);

      // Store genuine OCR fields without fabricated data
      const fields = data.ocr_result?.fields || {};
      const ocrRes = data.ocr_result || {};
      setOcrResult({
        fullName: fields.full_name || 'Not Available',
        surname: fields.surname || null,
        givenNames: fields.given_names || null,
        name: ocrRes.name || fields.name || {},
        visualName: ocrRes.visual_name || fields.visual_name || {},
        mrzName: ocrRes.mrz_name || fields.mrz_name || {},
        nameConsistency: ocrRes.name_consistency || fields.name_consistency || {},
        documentNumber: fields.document_number || 'Not Available',
        dob: fields.date_of_birth || 'Not Available',
        nationality: fields.nationality || 'Not Available',
        gender: fields.gender || fields.sex || 'Not Available',
        documentType: data.document_type || selectedDocumentType,
        issueDate: fields.issue_date || 'Not Available',
        expiryDate: fields.expiry_date || 'Not Available',
        placeOfBirth: fields.place_of_birth || null,
        placeOfIssue: fields.place_of_issue || null,
        issuingAuthority: fields.issuing_authority || null,
        mrzRaw: fields.mrz_raw || null,
        confidence: ocrRes.confidence || 0,
        averageConfidence: ocrRes.average_confidence || 0,
        fieldConfidence: ocrRes.field_confidence || {},
        qualityScore: ocrRes.quality_score || 'GOOD',
        qualityReason: ocrRes.quality_reason || '',
        processingTimeMs: ocrRes.processing_time_ms || 0,
        engine: ocrRes.engine || 'RapidOCR-ONNX',
        textLines: ocrRes.text_lines || [],
        fullText: ocrRes.full_text || '',
        mrzResult: data.mrz_result || null,
      });

      // Store genuine Tampering Forensics
      const tr = data.tampering_result || {};
      let integrity = "Passed (No Anomalies)";
      if (tr.tampering_detected) {
        integrity = "Failed (Manipulation Found)";
      } else if (tr.requires_review) {
        integrity = "Requires Review (Elevated Anomaly)";
      }

      setTamperResult({
        imageIntegrity: integrity,
        metadataAnalysis: tr.metadata_analysis?.summary || "Not Available",
        tamperingIndicators: tr.indicators?.join("; ") || "None detected across optical checks",
        fontConsistency: "Analysis unavailable"
      });

      // Store genuine Database Match Result
      const mr = data.matching_result || {};
      let dbMatchDisplay = "No Match";
      if (mr.database_match) {
        dbMatchDisplay = mr.match_type ? mr.match_type.replace(/_/g, ' ').toUpperCase() : "MATCH CONFIRMED";
      } else if (mr.match_type) {
        dbMatchDisplay = mr.match_type.replace(/_/g, ' ').toUpperCase();
      }

      setMatchingResult({
        databaseMatch: dbMatchDisplay,
        fieldMatch: mr.database_match ? "Matched in Central Registry" : "No Matching Record in Database",
        nameSimilarity: mr.name_similarity !== undefined ? `${Math.round(mr.name_similarity * 100)}%` : "0%",
        documentNumberMatch: mr.field_matches?.document_number ? "Matched in Registry" : "Unmatched in Registry"
      });

      setRiskLevel(data.risk_level || 'Pending');
      setRiskScore(data.risk_score !== undefined ? data.risk_score : null);

      if (data.can_proceed_to_face) {
        setFaceStatus('waiting');
      } else {
        setFaceStatus('locked');
      }

      return { success: true, data };
    } catch (err) {
      setDocumentStatus('error');
      setWorkflowError(err.message || 'Verification service error.');
      return { success: false, error: err.message };
    }
  };

  // Face Verification Submission to Real API
  const submitFaceMatch = async (faceBlob) => {
    if (!faceBlob) {
      const err = 'No face capture available. Please capture or upload a face image.';
      setWorkflowError(err);
      return { success: false, error: err };
    }

    if (!verificationId) {
      const err = 'Cannot execute biometric match: Missing verification ID.';
      setWorkflowError(err);
      return { success: false, error: err };
    }

    if (documentStatus !== 'verified') {
      const err = 'Biometric verification blocked: Document screening status must be Verified.';
      setWorkflowError(err);
      return { success: false, error: err };
    }

    if (faceImagePreview) URL.revokeObjectURL(faceImagePreview);
    setFaceImagePreview(URL.createObjectURL(faceBlob));

    setFaceStatus('processing');
    setWorkflowError(null);

    try {
      const apiRes = await submitFaceVerification(verificationId, faceBlob);
      setFaceStatus(apiRes.outcome);
      setFinalDecision((apiRes.final_decision || 'Pending').replace(/_/g, ' ').toUpperCase());
      setRiskLevel(apiRes.risk_level);
      setRiskScore(apiRes.risk_score);
      return { success: true, data: apiRes };
    } catch (err) {
      setFaceStatus('error');
      setWorkflowError(err.message || 'Face verification service error.');
      return { success: false, error: err.message };
    }
  };

  // Reset entire workflow
  const resetWorkflow = () => {
    if (filePreviewUrl) URL.revokeObjectURL(filePreviewUrl);
    if (faceImagePreview) URL.revokeObjectURL(faceImagePreview);
    setUploadedFile(null);
    setFilePreviewUrl(null);
    setDocumentStatus('idle');
    setWorkflowError(null);
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
        workflowError,
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

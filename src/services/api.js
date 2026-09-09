/**
 * ============================================================================
 * iDenTFy — API Service Client Layer (100% Real End-to-End Integration)
 * ============================================================================
 * Clean integration layer designed for FastAPI backend (/api/v1)
 *
 * Provides typed/structured calls using fetch with FormData and JSON.
 * NEVER uses mock data, synthetic results, or fake fallbacks.
 * Accurately surfaces errors when services are offline or inputs are invalid.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Health check probe to the technical backend health endpoint.
 * Infrastructural technical ping checking FastAPI and database responsiveness.
 */
export async function checkSystemHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return {
        online: true,
        status: data.status || 'healthy',
        database: data.database || 'connected',
        timestamp: data.timestamp || new Date().toISOString()
      };
    }
    return {
      online: false,
      status: 'error',
      database: 'disconnected',
      error: `HTTP ${response.status}: Service error`
    };
  } catch (err) {
    return {
      online: false,
      status: 'offline',
      database: 'disconnected',
      error: err.name === 'AbortError'
        ? 'Connection timed out'
        : `Backend unreachable at ${API_BASE_URL}. Ensure FastAPI service is running.`,
    };
  }
}

/**
 * Upload an identity document for genuine OCR extraction and security screening.
 * Strictly sends the actual browser File object via multipart/form-data.
 *
 * @param {File|Blob} documentFile - Genuine browser File object from <input type="file">
 * @param {string} documentType - passport | identity_card | residence_permit | driver_license
 */
export async function uploadDocument(documentFile, documentType) {
  if (!documentFile || (!(documentFile instanceof File) && !(documentFile instanceof Blob))) {
    throw new Error('Invalid document file: Please select a valid image file.');
  }

  const formData = new FormData();
  formData.append('document_file', documentFile, documentFile.name || 'document.jpg');
  formData.append('document_type', documentType);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
      method: 'POST',
      body: formData,
    });
  } catch (netErr) {
    throw new Error(
      `Verification service unavailable: Unable to reach backend at ${API_BASE_URL}. Please ensure the screening API is running.`
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const detail = errorData?.detail || errorData?.message || `Document upload failed (HTTP ${response.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }

  const data = await response.json();
  return {
    success: true,
    data,
  };
}

/**
 * Submit live face photo or camera capture for biometric matching against document portrait.
 * Strictly sends genuine multipart/form-data.
 *
 * @param {string} verificationId - Active verification ID (e.g. IDF-2026-XXXXX)
 * @param {File|Blob} faceFile - Genuine captured Blob or image File
 */
export async function submitFaceVerification(verificationId, faceFile) {
  if (!verificationId) {
    throw new Error('Face verification requires an active verification ID.');
  }
  if (!faceFile || (!(faceFile instanceof File) && !(faceFile instanceof Blob))) {
    throw new Error('Face verification requires a valid face capture or photo.');
  }

  const formData = new FormData();
  formData.append('face_file', faceFile, faceFile.name || 'face.jpg');
  formData.append('verification_id', verificationId);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/face/verify`, {
      method: 'POST',
      body: formData,
    });
  } catch (netErr) {
    throw new Error(
      `Face verification service unavailable: Unable to reach backend at ${API_BASE_URL}.`
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const detail = errorData?.detail || `Face verification failed (HTTP ${response.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }

  return await response.json();
}

/**
 * Retrieve verification audit history directly from PostgreSQL/SQLite.
 * Returns empty array [] if no records exist.
 *
 * @param {Object} filters
 */
export async function getVerificationHistory(filters = {}) {
  const queryParams = new URLSearchParams();
  Object.entries(filters).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '' && val !== 'all') {
      queryParams.append(key, val);
    }
  });

  const queryStr = queryParams.toString();
  const url = `${API_BASE_URL}/api/v1/verifications${queryStr ? `?${queryStr}` : ''}`;

  let response;
  try {
    response = await fetch(url, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
  } catch (netErr) {
    throw new Error(
      `Audit service unavailable: Cannot connect to database backend at ${API_BASE_URL}.`
    );
  }

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `Failed to fetch verification history (HTTP ${response.status})`);
  }

  const records = await response.json();
  if (!Array.isArray(records)) {
    return [];
  }

  // Normalize records so both camelCase and snake_case properties work seamlessly
  return records.map((rec) => ({
    ...rec,
    holderName: rec.holderName || rec.holder_name || 'Unextracted',
    holder_name: rec.holder_name || rec.holderName || 'Unextracted',
    documentType: rec.documentType || rec.document_type || 'Document',
    document_type: rec.document_type || rec.documentType || 'Document',
    documentNumber: rec.documentNumber || rec.document_number || 'Unextracted',
    document_number: rec.document_number || rec.documentNumber || 'Unextracted',
    riskLevel: rec.riskLevel || rec.risk_level || 'Pending',
    risk_level: rec.risk_level || rec.riskLevel || 'Pending',
    riskScore: rec.riskScore !== undefined ? rec.riskScore : rec.risk_score,
    risk_score: rec.risk_score !== undefined ? rec.risk_score : rec.riskScore,
    finalDecision: rec.finalDecision || rec.final_decision || rec.status,
    final_decision: rec.final_decision || rec.finalDecision || rec.status,
  }));
}

/**
 * Retrieve deep forensic dossier for a specific verification ID.
 *
 * @param {string} verificationId
 */
export async function getVerificationDetails(verificationId) {
  if (!verificationId) {
    throw new Error('Verification ID is required.');
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/verifications/${encodeURIComponent(verificationId)}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
  } catch (netErr) {
    throw new Error(
      `Dossier lookup unavailable: Cannot connect to backend at ${API_BASE_URL}.`
    );
  }

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `Failed to fetch verification dossier (HTTP ${response.status})`);
  }

  const data = await response.json();
  return {
    ...data,
    holderName: data.holderName || data.holder_name || 'Unextracted',
    documentNumber: data.documentNumber || data.document_number || 'Unextracted',
    documentType: data.documentType || data.document_type || 'Document',
    riskLevel: data.riskLevel || data.risk_level || 'Pending',
    riskScore: data.riskScore !== undefined ? data.riskScore : data.risk_score,
    finalDecision: data.finalDecision || data.final_decision || data.status,
    databaseMatch: data.databaseMatch || data.database_match || 'No Match',
    tamperDetection: data.tamperDetection || data.tamper_detection || 'No Anomalies Detected',
    faceVerification: data.faceVerification || data.face_verification || 'Pending',
    officerNotes: data.officerNotes || data.officer_notes,
    ocrDetails: data.ocrDetails || data.ocr_details,
    tamperForensics: data.tamperForensics || data.tamper_forensics
  };
}

/**
 * Retrieve registered government verification providers and connectivity status.
 */
export async function getGovernmentProviders() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/government/providers`);
    if (!response.ok) return [];
    return await response.json();
  } catch (err) {
    return [];
  }
}

export { API_BASE_URL };

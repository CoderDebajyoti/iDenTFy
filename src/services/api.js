/**
 * ============================================================================
 * iDenTFy — API Service Client Layer
 * ============================================================================
 * Clean integration layer designed for FastAPI backend (/api/v1)
 *
 * Provides typed/structured calls using fetch with FormData and JSON.
 * Gracefully handles offline or mock states when backend is not running.
 */

import { MOCK_VERIFICATION_HISTORY, PRESET_SCENARIOS } from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Health check probe to the technical backend health endpoint.
 * NOTE: As per system requirements, this is solely an infrastructure ping,
 * NOT a medical or health verification feature.
 */
export async function checkSystemHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return { online: true, status: data.status || 'healthy', timestamp: new Date().toISOString() };
    }
    return { online: false, status: 'error', error: `HTTP ${response.status}` };
  } catch (err) {
    return {
      online: false,
      status: 'offline',
      error: err.name === 'AbortError' ? 'Timeout' : 'Backend unreachable (FastAPI offline)',
    };
  }
}

/**
 * Upload an identity document for OCR extraction and initial security screening.
 * Strictly sends the genuine browser File object via multipart/form-data.
 *
 * @param {File} documentFile - Genuine browser File object from <input type="file">
 * @param {string} documentType - passport | id_card | residence_permit | driver_license
 */
export async function uploadDocument(documentFile, documentType) {
  if (!(documentFile instanceof File)) {
    throw new Error('Invalid document file: Must be an instance of browser File.');
  }

  const formData = new FormData();
  formData.append('document_file', documentFile);
  formData.append('document_type', documentType);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/document/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Upload failed with status ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      source: 'api',
      data,
    };
  } catch (err) {
    // If backend is not running or error occurs, return structured error/fallback
    return {
      success: false,
      source: 'offline_fallback',
      error: err.message,
      // Provide clean simulated result for testing when backend is not running
      data: null,
    };
  }
}

/**
 * Submit face photo or camera capture for biometric matching against document portrait.
 *
 * @param {string} verificationId
 * @param {File|Blob} faceFile
 */
export async function submitFaceVerification(verificationId, faceFile) {
  const formData = new FormData();
  if (faceFile) {
    formData.append('face_file', faceFile);
  }
  formData.append('verification_id', verificationId);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/face/verify`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Face verification failed with status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    return {
      success: false,
      error: err.message,
      source: 'offline_fallback',
    };
  }
}

/**
 * Retrieve verification history with optional filtering.
 */
export async function getVerificationHistory(filters = {}) {
  try {
    const query = new URLSearchParams(filters).toString();
    const response = await fetch(`${API_BASE_URL}/api/v1/verifications?${query}`);
    if (response.ok) {
      return await response.json();
    }
  } catch {
    // Fall back to structured mock data for UI development
  }
  return MOCK_VERIFICATION_HISTORY;
}

/**
 * Retrieve deep forensic dossier for a specific verification ID.
 */
export async function getVerificationDetails(verificationId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/verifications/${verificationId}`);
    if (response.ok) {
      return await response.json();
    }
  } catch {
    // Fall back to mock lookup
  }
  const found = MOCK_VERIFICATION_HISTORY.find((item) => item.id === verificationId);
  return found || MOCK_VERIFICATION_HISTORY[0];
}

export { API_BASE_URL };

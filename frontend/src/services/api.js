const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function verifyDocument(
  documentType,
  documentFile
) {
  const formData = new FormData();

  formData.append("document_type", documentType);
  formData.append("document_file", documentFile);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/document/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    let errorDetail = "Verification failed";
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch (e) {}
    throw new Error(errorDetail);
  }

  return await response.json();
}
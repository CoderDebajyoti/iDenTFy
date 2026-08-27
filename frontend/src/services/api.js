const API_BASE_URL = "http://127.0.0.1:8000";

export async function verifyDocument(
  documentType,
  documentFile,
  faceFile
) {
  const formData = new FormData();

  formData.append("document_type", documentType);
  formData.append("document", documentFile);

  if (faceFile) {
    formData.append("face", faceFile);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/verify`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error("Verification failed");
  }

  return await response.json();
}
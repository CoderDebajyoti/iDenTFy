import { useState } from "react";
import UploadBox from "../components/UploadBox";
import ResultCard from "../components/ResultCard";

const DOCUMENT_TYPES = [
  {
    id: "identity_card",
    name: "Identity Card",
    icon: "▣",
  },
  {
    id: "passport",
    name: "Passport",
    icon: "▤",
  },
  {
    id: "residence_permit",
    name: "Residence Permit",
    icon: "▰",
  },
  {
    id: "driver_license",
    name: "Driver License",
    icon: "▰",
  },
];

function Home() {
  const [step, setStep] = useState(1);
  const [selectedType, setSelectedType] = useState("identity_card");

  const [documentFile, setDocumentFile] = useState(null);
  const [faceFile, setFaceFile] = useState(null);

  const [processing, setProcessing] = useState(false);

  const [result, setResult] = useState(null);

  const selectedDocument = DOCUMENT_TYPES.find(
    (doc) => doc.id === selectedType
  );

  // -----------------------------
  // STEP 1 → STEP 2
  // -----------------------------
  const handleContinueDocumentType = () => {
    if (!selectedType) {
      return;
    }

    setStep(2);
  };

  // -----------------------------
  // STEP 2 → STEP 3
  // -----------------------------
  const handleVerify = async () => {
    if (!documentFile) {
      alert("Please upload your document first.");
      return;
    }

    setProcessing(true);

    /*
      Later you will replace this mock processing
      with your FastAPI API call.

      Example:
      const response = await verifyDocument(
        selectedType,
        documentFile,
        faceFile
      );
    */

    setTimeout(() => {
      const faceProvided = !!faceFile;

      setResult({
        documentType: selectedDocument.name,

        documentTypeCheck: {
          status: "passed",
          selected: selectedDocument.name,
          detected: selectedDocument.name,
        },

        ocr: {
          status: "passed",
          name: "Rahul Kumar",
          dateOfBirth: "10/05/2000",
          documentNumber: "XXXXXXXXXX",
          nationality: "Indian",
        },

        tamper: {
          status: "passed",
          message: "No signs of document manipulation detected.",
        },

        face: {
          provided: faceProvided,
          status: faceProvided ? "passed" : "skipped",
          score: faceProvided ? 94.6 : null,
        },

        riskScore: faceProvided ? 8 : 15,

        overallStatus: "passed",
      });

      setProcessing(false);
      setStep(3);
    }, 2000);
  };

  // -----------------------------
  // RESET
  // -----------------------------
  const handleStartAgain = () => {
    setStep(1);
    setSelectedType("identity_card");
    setDocumentFile(null);
    setFaceFile(null);
    setResult(null);
  };

  return (
    <div className="app-container">

      {/* ================= HEADER ================= */}

      <header className="app-header">

        <button
          className="back-button"
          onClick={() => {
            if (step > 1) {
              setStep(step - 1);
            }
          }}
          disabled={step === 1}
        >
          ←
        </button>

        <div className="brand">
          <span className="brand-i">i</span>Den<span className="brand-fy">Fy</span>
        </div>

        <button className="language-button">
          ◉
        </button>

      </header>


      {/* ================= STEP INDICATOR ================= */}

      <div className="step-indicator">

        <div className={`step-item ${step >= 1 ? "active" : ""}`}>
          <div className="step-circle">1</div>
          <span>Document Type</span>
        </div>

        <div className="step-line"></div>

        <div className={`step-item ${step >= 2 ? "active" : ""}`}>
          <div className="step-circle">2</div>
          <span>Verification</span>
        </div>

        <div className="step-line"></div>

        <div className={`step-item ${step >= 3 ? "active" : ""}`}>
          <div className="step-circle">3</div>
          <span>Results</span>
        </div>

      </div>


      {/* ================= STEP 1 ================= */}

      {step === 1 && (
        <section className="page-section document-type-page">

          <div className="page-title">

            <div className="security-icon">
              🛡
            </div>

            <h1>Select document type</h1>

            <p>
              Which document would you want to identify?
            </p>

          </div>


          <div className="document-type-card">

            {DOCUMENT_TYPES.map((document) => (

              <button
                key={document.id}
                className={`document-type-option ${
                  selectedType === document.id ? "selected" : ""
                }`}
                onClick={() => setSelectedType(document.id)}
              >

                <div className="document-option-left">

                  <span className="document-icon">
                    {document.icon}
                  </span>

                  <span>
                    {document.name}
                  </span>

                </div>

                {selectedType === document.id && (
                  <span className="check-icon">
                    ✓
                  </span>
                )}

              </button>

            ))}

          </div>


          <button
            className="primary-button continue-button"
            onClick={handleContinueDocumentType}
          >
            CONTINUE
          </button>

        </section>
      )}


      {/* ================= STEP 2 ================= */}

      {step === 2 && (
        <section className="page-section verification-page">

          <div className="page-title">

            <div className="security-icon">
              🛡
            </div>

            <h1>Identity Verification</h1>

            <p>
              Secure verification in just two simple steps
            </p>

            <div className="selected-document-badge">
              Selected: <strong>{selectedDocument.name}</strong>
            </div>

          </div>


          <div className="verification-grid">

            {/* DOCUMENT */}

            <div className="verification-card">

              <div className="verification-icon document-big-icon">
                ▤
              </div>

              <h2>Document Verification</h2>

              <p>
                Capture your identity document
              </p>


              <UploadBox
                title="Upload Document"
                file={documentFile}
                setFile={setDocumentFile}
                accept="image/*,.pdf"
              />

            </div>


            {/* FACE */}

            <div className="verification-card">

              <div className="verification-icon face-big-icon">
                ♙
              </div>

              <h2>Face Verification</h2>

              <p>
                Optional face matching
              </p>


              <UploadBox
                title="Upload Face"
                file={faceFile}
                setFile={setFaceFile}
                accept="image/*"
                optional={true}
              />

            </div>

          </div>


          {/* VERIFY BUTTON */}

          <button
            className="primary-button verify-button"
            onClick={handleVerify}
            disabled={!documentFile || processing}
          >

            {processing ? (
              <>
                <span className="spinner"></span>
                VERIFYING...
              </>
            ) : (
              "VERIFY DOCUMENT"
            )}

          </button>


          {/* SECURITY MESSAGE */}

          <div className="secure-box">

            <div className="secure-title">
              <span>✓</span>
              Secure & Private
            </div>

            <p>
              🔒 Your biometric data is encrypted and automatically
              deleted after verification.
            </p>

          </div>

        </section>
      )}


      {/* ================= STEP 3 ================= */}

      {step === 3 && result && (

        <section className="page-section results-page">

          <div className="page-title">

            <div className="result-success-icon">
              ✓
            </div>

            <h1>Verification Results</h1>

            <p>
              Your identity verification has been completed.
            </p>

          </div>


          {/* OVERALL RESULT */}

          <div className="overall-result-card">

            <div>

              <span className="result-label">
                OVERALL STATUS
              </span>

              <h2>
                ✓ Verification Passed
              </h2>

              <p>
                {result.documentType} verification completed successfully.
              </p>

            </div>


            <div className="risk-score">

              <span>Risk Score</span>

              <strong>
                {result.riskScore}
              </strong>

              <small>Low Risk</small>

            </div>

          </div>


          {/* RESULT CARDS */}

          <div className="results-grid">

            <ResultCard
              icon="▤"
              title="Document Type"
              status="passed"
              value={result.documentType}
              description="Selected and detected document type match."
            />


            <ResultCard
              icon="OCR"
              title="OCR Verification"
              status={result.ocr.status}
              value="Information Extracted"
              description="Name, date of birth and document number extracted."
            />


            <ResultCard
              icon="✓"
              title="Tamper Detection"
              status={result.tamper.status}
              value="No Tampering Detected"
              description={result.tamper.message}
            />


            <ResultCard
              icon="♙"
              title="Face Verification"
              status={result.face.status}
              value={
                result.face.provided
                  ? `Match ${result.face.score}%`
                  : "Skipped"
              }
              description={
                result.face.provided
                  ? "Document photo and provided face matched."
                  : "No face was provided. Face verification was optional."
              }
            />

          </div>


          {/* OCR DETAILS */}

          <div className="details-card">

            <div className="details-header">

              <h2>Extracted Document Information</h2>

              <span className="status-pill passed">
                ✓ Verified
              </span>

            </div>


            <div className="details-grid">

              <div className="detail-item">
                <span>Full Name</span>
                <strong>{result.ocr.name}</strong>
              </div>

              <div className="detail-item">
                <span>Date of Birth</span>
                <strong>{result.ocr.dateOfBirth}</strong>
              </div>

              <div className="detail-item">
                <span>Document Number</span>
                <strong>{result.ocr.documentNumber}</strong>
              </div>

              <div className="detail-item">
                <span>Nationality</span>
                <strong>{result.ocr.nationality}</strong>
              </div>

            </div>

          </div>


          <button
            className="primary-button start-again-button"
            onClick={handleStartAgain}
          >
            START NEW VERIFICATION
          </button>

        </section>

      )}

    </div>
  );
}

export default Home;
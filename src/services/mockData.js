/**
 * ============================================================================
 * iDenTFy — Mock & Diagnostic Dataset for UI Presentation & Testing
 * ============================================================================
 * NOTE: These mock records are strictly isolated for:
 * 1. Verification History page table population during development/demo
 * 2. Scenario testing toggles (Verified, Requires Review, Tampered, Failed)
 * 3. Individual record dossier view (/history/:id)
 *
 * All mock data is clearly separated and will be superseded once FastAPI endpoints
 * with database persistence are activated.
 */

export const MOCK_VERIFICATION_HISTORY = [
  {
    id: "IDF-2026-8891A",
    timestamp: "2026-09-05 14:32:10 UTC",
    documentType: "Passport",
    holderName: "AARAV SHARMA",
    documentNumber: "Z6549210",
    nationality: "IND",
    status: "Verified",
    riskLevel: "Low",
    riskScore: 12,
    documentStatus: "Passed",
    databaseMatch: "100% Match",
    tamperDetection: "No Anomalies Detected",
    faceVerification: "Matched (98.4%)",
    finalDecision: "Verified",
    officerNotes: "Indian Passport verified at Immigration Check Post (ICP Delhi Terminal 3). Biometrics authentic.",
    ocrDetails: {
      fullName: "AARAV SHARMA",
      documentNumber: "Z6549210",
      dob: "1995-08-15",
      nationality: "IND / India",
      documentType: "Passport (P)",
      issueDate: "2020-08-15",
      expiryDate: "2030-08-14",
      mrzRaw: "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<\nZ6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    },
    tamperForensics: {
      imageIntegrity: "Passed (100%)",
      metadataAnalysis: "Clean EXIF / Original Optical Scanner Capture",
      tamperingIndicators: "None",
      fontConsistency: "Official Security Printing & Indian Passport typography compliant",
      blurScore: "Sharp (Laplacian variance: 842.1)",
      lightingScore: "Optimal (Mean brightness: 142.3)"
    }
  },
  {
    id: "IDF-2026-8892B",
    timestamp: "2026-09-05 15:10:45 UTC",
    documentType: "Identity Card",
    holderName: "PRIYA PATEL",
    documentNumber: "ID5502914",
    nationality: "IND",
    status: "Requires Review",
    riskLevel: "Medium",
    riskScore: 48,
    documentStatus: "Review Required",
    databaseMatch: "Discrepancy (DOB Mismatch)",
    tamperDetection: "Minor Font Inconsistency",
    faceVerification: "Matched (89.1%)",
    finalDecision: "Requires Review",
    officerNotes: "Secondary inspection recommended: birth date does not match national citizen registry record.",
    ocrDetails: {
      fullName: "PRIYA PATEL",
      documentNumber: "ID5502914",
      dob: "1991-11-23",
      nationality: "IND / India",
      documentType: "National ID (Aadhaar / Voter ID)",
      issueDate: "2019-02-15",
      expiryDate: "2029-02-14",
      mrzRaw: "I<IND5502914<<8<<<<<<<<<<<<<<<\n9111234F2902148IND<<<<<<<<<<<4PATEL<<PRIYA<<<<<<<<<<<<<"
    },
    tamperForensics: {
      imageIntegrity: "Warning (Minor artifacting)",
      metadataAnalysis: "Software tag: GIMP 2.10 detected in metadata",
      tamperingIndicators: "Pixel discrepancy around expiration numeral",
      fontConsistency: "Font weight varies in date block",
      blurScore: "Acceptable (Variance: 480.2)",
      lightingScore: "Slight glare on laminate surface"
    }
  },
  {
    id: "IDF-2026-8893C",
    timestamp: "2026-09-05 16:45:02 UTC",
    documentType: "Driver License",
    holderName: "VIKRAM SINGH",
    documentNumber: "DL04202300789",
    nationality: "IND",
    status: "Verification Failed",
    riskLevel: "High",
    riskScore: 92,
    documentStatus: "Failed (Tampered / Blacklisted)",
    databaseMatch: "Registry Alert: Blacklisted / Suspicious",
    tamperDetection: "High Probability of Photo Replacement",
    faceVerification: "Not Matched (41.2%)",
    finalDecision: "Verification Failed",
    officerNotes: "FRAUD ALERT: Driving licence photo manipulation detected. Subject face does not match document portrait.",
    ocrDetails: {
      fullName: "VIKRAM SINGH",
      documentNumber: "DL04202300789",
      dob: "1985-08-30",
      nationality: "IND / India",
      documentType: "Driver License (Sarathi / MoRTH)",
      issueDate: "2021-01-12",
      expiryDate: "2031-01-11",
      mrzRaw: "D1IND04202300789<<<<<<<<<<<<<<\n8508302M3101114IND<<<<<<<<<<<2SINGH<<VIKRAM<<<<<<<<<<<<<"
    },
    tamperForensics: {
      imageIntegrity: "Failed: Splicing / ELA edge anomalies",
      metadataAnalysis: "Multiple save generations detected",
      tamperingIndicators: "Inconsistent noise pattern around photo perimeter",
      fontConsistency: "Incorrect tracking on license number",
      blurScore: "High blur around portrait area",
      lightingScore: "Mismatched ambient illumination"
    }
  },
  {
    id: "IDF-2026-8894D",
    timestamp: "2026-09-05 18:05:19 UTC",
    documentType: "Passport",
    holderName: "RAJESH VERMA",
    documentNumber: "Z1102945",
    nationality: "IND",
    status: "Verification Failed",
    riskLevel: "High",
    riskScore: 85,
    documentStatus: "Failed (Expired Document)",
    databaseMatch: "100% Match (Registry Status: Expired)",
    tamperDetection: "No Tampering Found",
    faceVerification: "Verification Blocked (Document Expired)",
    finalDecision: "Verification Failed",
    officerNotes: "Travel document expired on 2022-01-09. Biometric progression halted per immigration screening rules.",
    ocrDetails: {
      fullName: "RAJESH VERMA",
      documentNumber: "Z1102945",
      dob: "1980-05-12",
      nationality: "IND / India",
      documentType: "Passport (P)",
      issueDate: "2012-01-10",
      expiryDate: "2022-01-09",
      mrzRaw: "P<INDVERMA<<RAJESH<<<<<<<<<<<<<<<<<<<<<<<<<<\nZ11029455IND8005124M2201091<<<<<<<<<<<<<<06"
    },
    tamperForensics: {
      imageIntegrity: "Passed (100%)",
      metadataAnalysis: "Clean optical scan metadata",
      tamperingIndicators: "None",
      fontConsistency: "Official ICAO 9303 compliant",
      blurScore: "Sharp (Variance: 790.5)",
      lightingScore: "Balanced (Mean: 138.0)"
    }
  },
  {
    id: "IDF-2026-8895E",
    timestamp: "2026-09-05 19:22:40 UTC",
    documentType: "Passport",
    holderName: "DAVID K. MILLER",
    documentNumber: "PA4401829",
    nationality: "GBR",
    status: "Requires Review",
    riskLevel: "Medium",
    riskScore: 38,
    documentStatus: "Review Required",
    databaseMatch: "Matched (Indian e-Visa Verification)",
    tamperDetection: "No Tampering Detected",
    faceVerification: "Matched (94.2%)",
    finalDecision: "Requires Review",
    officerNotes: "Foreign national entering on Indian e-Tourist Visa. Secondary check advised for visa validity endorsement.",
    ocrDetails: {
      fullName: "DAVID K. MILLER",
      documentNumber: "PA4401829",
      dob: "1986-04-18",
      nationality: "GBR / United Kingdom",
      documentType: "Passport & Indian e-Visa",
      issueDate: "2021-08-11",
      expiryDate: "2031-08-10",
      mrzRaw: "P<GBRMILLER<<DAVID<K<<<<<<<<<<<<<<<<<<<<<<<<\nPA44018293GBR8604182M3108106<<<<<<<<<<<<<<08"
    },
    tamperForensics: {
      imageIntegrity: "Warning: High specular reflection",
      metadataAnalysis: "Device: High-res flatbed scanner",
      tamperingIndicators: "Glare over security foil ribbon",
      fontConsistency: "Compliant font kerning",
      blurScore: "Sharp (Variance: 650.0)",
      lightingScore: "Overexposed in upper right sector"
    }
  }
];

export const PRESET_SCENARIOS = {
  verified: {
    status: "Verified",
    riskLevel: "Low",
    riskScore: 14,
    documentStatus: "Passed",
    databaseMatch: "Database Match Confirmed",
    tamperDetection: "No Alterations Detected",
    faceVerification: "Matched (97.9%)",
    finalDecision: "Verified",
    ocrDetails: {
      fullName: "AARAV SHARMA",
      documentNumber: "Z6549210",
      dob: "1995-08-15",
      nationality: "IND / India",
      documentType: "Passport",
      issueDate: "2020-08-15",
      expiryDate: "2030-08-14",
      mrzRaw: "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<\nZ6549210<2IND9508152M3008144<<<<<<<<<<<<<<08"
    },
    tamperForensics: {
      imageIntegrity: "Valid / Clean",
      metadataAnalysis: "Original unmodified camera capture",
      tamperingIndicators: "None detected across color channels",
      fontConsistency: "Compliant with standard typography specifications"
    }
  },
  review: {
    status: "Requires Review",
    riskLevel: "Medium",
    riskScore: 52,
    documentStatus: "Review Required",
    databaseMatch: "Partial Match (Field Discrepancy)",
    tamperDetection: "Suspicious Edge Gradient Around Photo",
    faceVerification: "Borderline Similarity (74.2%)",
    finalDecision: "Requires Review",
    ocrDetails: {
      fullName: "PRIYA PATEL",
      documentNumber: "ID5502914",
      dob: "1991-11-23",
      nationality: "IND / India",
      documentType: "National ID Card",
      issueDate: "2019-02-15",
      expiryDate: "2029-02-14",
      mrzRaw: "I<IND5502914<<8<<<<<<<<<<<<<<<\n9111234F2902148IND<<<<<<<<<<<4PATEL<<PRIYA<<<<<<<<<<<<<"
    },
    tamperForensics: {
      imageIntegrity: "Warning: Discontinuous pixel gradients",
      metadataAnalysis: "EXIF indicates editing tool traces",
      tamperingIndicators: "Resampling artifacts detected in date field",
      fontConsistency: "Letter spacing deviates from standard template"
    }
  },
  failed: {
    status: "Not Verified",
    riskLevel: "High",
    riskScore: 94,
    documentStatus: "Failed / Forgery Suspected",
    databaseMatch: "Database Mismatch (Invalid Checksum)",
    tamperDetection: "Severe Splicing & Digital Manipulation",
    faceVerification: "Not Matched (32.1%)",
    finalDecision: "Verification Failed",
    ocrDetails: {
      fullName: "VIKRAM SINGH",
      documentNumber: "Z0009999",
      dob: "1978-09-13",
      nationality: "IND / India",
      documentType: "Passport",
      issueDate: "2023-01-01",
      expiryDate: "2033-01-01",
      mrzRaw: "P<INDSINGH<<VIKRAM<<<<<<<<<<<<<<<<<<<<<<<<<<\nZ00099994IND7809139M3301018<<<<<<<<<<<<<<99"
    },
    tamperForensics: {
      imageIntegrity: "Failed: Obvious copy-paste cloning marks",
      metadataAnalysis: "Stripped metadata / mismatched DPI",
      tamperingIndicators: "High error level analysis (ELA) response in photo zone",
      fontConsistency: "Wrong font family used in primary surname field"
    }
  }
};

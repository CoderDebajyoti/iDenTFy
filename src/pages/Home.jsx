import React from 'react';
import { Link } from 'react-router-dom';
import {
  Shield,
  ShieldCheck,
  ScanText,
  Database,
  ShieldAlert,
  UserCheck,
  ArrowRight,
  History,
  FileCheck2,
  Sparkles,
  CheckCircle2,
  Lock,
  Cpu,
  Layers,
  Fingerprint
} from 'lucide-react';
import Button from '../components/common/Button';

export default function Home() {
  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Hero Section */}
      <section className="landing-hero">
        <div>
          <div className="hero-badge">
            <Sparkles size={14} />
            <span>Ministry of Home Affairs • Smart India Hackathon (SIH)</span>
          </div>

          <h1 className="hero-title">
            AI-Powered Identity & <br />
            <span className="highlight-ai">Document Screening</span>
          </h1>

          <p className="hero-subtitle">
            Detect forged credentials, identify digital tampering, and verify citizen identities
            with enterprise OCR extraction, copy-move forensic screening, and 1:1 biometric facial confirmation.
          </p>

          <div className="hero-actions">
            <Link to="/verify/document">
              <Button variant="primary" size="lg" icon={FileCheck2}>
                Start New Screening
              </Button>
            </Link>

            <Link to="/history">
              <Button variant="secondary" size="lg" icon={History}>
                Audit History
              </Button>
            </Link>
          </div>

          {/* Key Stat Badges Ticker */}
          <div className="hero-stats-row">
            <div className="stat-item">
              <div className="stat-num">
                ICAO 9303
              </div>
              <div className="stat-lbl">
                Passports & National ID Standard
              </div>
            </div>
            <div className="stat-divider" />
            <div className="stat-item">
              <div className="stat-num highlight-blue">
                Multi-Spectral
              </div>
              <div className="stat-lbl">
                Tamper Anomaly Forensics
              </div>
            </div>
            <div className="stat-divider" />
            <div className="stat-item">
              <div className="stat-num highlight-emerald">
                1:1 Biometric
              </div>
              <div className="stat-lbl">
                Facial Match Confirmation
              </div>
            </div>
          </div>
        </div>

        {/* Holographic Document Intelligence Visual */}
        <div className="hero-visual-canvas">
          {/* Floating AI Badges */}
          <div className="hero-floating-badge floating-ocr">
            <ScanText size={15} style={{ color: '#38bdf8' }} />
            <span>PaddleOCR • 99.2% Accuracy</span>
          </div>

          <div className="hero-floating-badge floating-tamper">
            <ShieldCheck size={15} style={{ color: '#34d399' }} />
            <span>Zero Forensic Splicing</span>
          </div>

          {/* Holographic Credential Mock Card */}
          <div className="passport-mock-card">
            <div className="passport-scan-bar" />

            <div className="passport-header-mock">
              <span className="mock-country">REPUBLIC OF INDIA • भारत गणराज्य</span>
              <span className="mock-doc-type">
                PASSPORT &lt; IND
              </span>
            </div>

            <div className="mock-body-grid">
              <div className="mock-photo-box">
                <UserCheck size={42} strokeWidth={1.5} />
                <div className="mock-face-mesh" />
              </div>

              <div className="mock-details-col">
                <div className="mock-line-row">
                  <span className="mock-field-lbl">SURNAME & GIVEN NAMES</span>
                  <span className="mock-field-val">SHARMA, AARAV</span>
                </div>

                <div className="mock-line-row">
                  <span className="mock-field-lbl">PASSPORT NUMBER</span>
                  <span className="mock-field-val" style={{ color: '#38bdf8' }}>Z6549210</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <div className="mock-line-row">
                    <span className="mock-field-lbl">NATIONALITY</span>
                    <span className="mock-field-val">IND</span>
                  </div>
                  <div className="mock-line-row">
                    <span className="mock-field-lbl">DATE OF BIRTH</span>
                    <span className="mock-field-val">15 AUG 1995</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mock-mrz-zone">
              P&lt;INDSHARMA&lt;&lt;AARAV&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;<br />
              Z6549210&lt;2IND9508152M3008144&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;08
            </div>
          </div>
        </div>
      </section>

      {/* System Capabilities 4-Grid */}
      <section className="section-capabilities">
        <div className="section-header-center">
          <div className="section-tag">Core Engine Features</div>
          <h2 className="section-title">Automated Document Defense Architecture</h2>
          <p style={{ fontSize: '0.94rem', color: 'var(--text-muted)', marginTop: '8px', maxWidth: '620px', margin: '8px auto 0' }}>
            Multi-layered forensic verification combining machine vision, cryptographical matching, and neural biometrics.
          </p>
        </div>

        <div className="capability-grid">
          {/* Card 1 */}
          <div className="capability-card">
            <div className="capability-icon cap-blue">
              <ScanText size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '8px' }}>
                OCR & Field Parsing
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                Advanced neural text recognition parses complex visual fields, validates checksum digits,
                and extracts machine-readable zone (MRZ) lines with high precision.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="capability-card">
            <div className="capability-icon cap-indigo">
              <Database size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '8px' }}>
                Database Cross-Matching
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                Cross-references extracted credentials against central security registries,
                fuzzy-matches identity names, and verifies document template rules.
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="capability-card">
            <div className="capability-icon cap-amber">
              <ShieldAlert size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '8px' }}>
                Tamper Forensics
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                Error level analysis (ELA), copy-paste forensic heuristics, and typographic kerning
                detect altered dates, swapped portraits, and manipulated text lines.
              </p>
            </div>
          </div>

          {/* Card 4 */}
          <div className="capability-card">
            <div className="capability-icon cap-purple">
              <Fingerprint size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '8px' }}>
                1:1 Face Biometrics
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                Executes 1:1 facial biometric matching between the document photo and a live camera
                capture of the subject to prevent impersonation and identity spoofing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5-Step Pipeline Flow */}
      <section className="section-workflow">
        <div className="section-header-center">
          <div className="section-tag">Verification Pipeline</div>
          <h2 className="section-title">How The Screening Engine Works</h2>
          <p style={{ fontSize: '0.94rem', color: 'var(--text-muted)', marginTop: '8px', maxWidth: '600px', margin: '8px auto 0' }}>
            A rigorous 5-stage pipeline ensuring zero fraudulent or compromised documents pass through screening
          </p>
        </div>

        <div className="workflow-steps-row">
          <div className="workflow-step-card">
            <span className="step-num-pill">01</span>
            <h4 className="step-card-title">Upload Document</h4>
            <p className="step-card-desc">
              Officer uploads a high-resolution scan or photo of Passport, National ID, or Driver License.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">02</span>
            <h4 className="step-card-title">OCR & Forensics</h4>
            <p className="step-card-desc">
              Optical engine performs image normalization, field extraction, and MRZ checksum validation.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">03</span>
            <h4 className="step-card-title">Registry Match</h4>
            <p className="step-card-desc">
              Extracted fields are cross-checked against authorized government databases for consistency.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">04</span>
            <h4 className="step-card-title">Face Verification</h4>
            <p className="step-card-desc">
              Upon document integrity pass, live facial biometric capture is matched with document portrait.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">05</span>
            <h4 className="step-card-title">Decision Dossier</h4>
            <p className="step-card-desc">
              Forensic engine synthesizes all risk indicators into a final determination and audit dossier.
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <Link to="/verify/document">
            <Button variant="primary" size="lg" icon={ArrowRight}>
              Initiate Document Screening
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}

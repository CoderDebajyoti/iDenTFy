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
  Lock
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
            Detect forged documents, identify inconsistencies, and verify identities
            with AI-powered document analysis, optical forensic screening, and biometric face matching.
          </p>

          <div className="hero-actions">
            <Link to="/verify/document">
              <Button variant="primary" size="lg" icon={FileCheck2}>
                Start Verification
              </Button>
            </Link>

            <Link to="/history">
              <Button variant="secondary" size="lg" icon={History}>
                View Verification History
              </Button>
            </Link>
          </div>

          {/* Key Stat Badges */}
          <div style={{ display: 'flex', gap: '24px', marginTop: '36px' }}>
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-brand-navy)' }}>
                ICAO 9303
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Indian Passport & Global Standard
              </div>
            </div>
            <div style={{ width: '1px', background: 'var(--border-subtle)' }} />
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#2563eb' }}>
                Multi-Spectral
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Tamper Anomaly Detection
              </div>
            </div>
            <div style={{ width: '1px', background: 'var(--border-subtle)' }} />
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--color-success)' }}>
                1:1 Biometric
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Face Verification Match
              </div>
            </div>
          </div>
        </div>

        {/* Sophisticated Abstract Document Intelligence Visual */}
        <div className="hero-visual-canvas">
          {/* Floating AI Badges */}
          <div className="hero-floating-badge floating-ocr">
            <ScanText size={14} style={{ color: '#38bdf8' }} />
            <span>PaddleOCR • 99.2% Confidence</span>
          </div>

          <div className="hero-floating-badge floating-tamper">
            <ShieldCheck size={14} style={{ color: '#34d399' }} />
            <span>Zero Forensic Splicing</span>
          </div>

          {/* Realistic Holographic Indian Document Card */}
          <div className="passport-mock-card">
            <div className="passport-scan-bar" />

            <div className="passport-header-mock">
              <span className="mock-country">REPUBLIC OF INDIA • भारत गणराज्य</span>
              <span style={{ fontSize: '0.72rem', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
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

      {/* System Overview 4 Capabilities Section */}
      <section className="section-capabilities">
        <div className="section-header-center">
          <div className="section-tag">Core Engine Features</div>
          <h2 className="section-title">Automated Document Defense Architecture</h2>
        </div>

        <div className="capability-grid">
          {/* Card 1 */}
          <div className="capability-card">
            <div className="capability-icon cap-blue">
              <ScanText size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '6px' }}>
                OCR & Document Processing
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Advanced neural text recognition parses complex visual fields, validates checksum digits,
                and extracts machine-readable zone (MRZ) data lines with high precision.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="capability-card">
            <div className="capability-icon cap-indigo">
              <Database size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '6px' }}>
                Document Matching
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Cross-references extracted credentials against central border control databases,
                fuzzy-matches identity names, and verifies document template formatting rules.
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="capability-card">
            <div className="capability-icon cap-amber">
              <ShieldAlert size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '6px' }}>
                Tamper Detection
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Error level analysis (ELA), digital copy-paste forensics, and typographic kerning
                heuristics flag altered dates, swapped portraits, and manipulated security fibers.
              </p>
            </div>
          </div>

          {/* Card 4 */}
          <div className="capability-card">
            <div className="capability-icon cap-purple">
              <UserCheck size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '6px' }}>
                Face Verification
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Executes 1:1 facial biometric matching between the document photo and a live camera
                capture of the subject to prevent impersonation and identity fraud.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works 5-Step Flow */}
      <section className="section-workflow">
        <div className="section-header-center">
          <div className="section-tag">Verification Lifecycle</div>
          <h2 className="section-title">How The System Works</h2>
          <p style={{ fontSize: '0.92rem', color: 'var(--text-muted)', marginTop: '8px', maxWidth: '600px', margin: '8px auto 0' }}>
            A rigorous 5-stage pipeline ensuring zero compromised documents pass through screening
          </p>
        </div>

        <div className="workflow-steps-row">
          <div className="workflow-step-card">
            <span className="step-num-pill">01</span>
            <h4 className="step-card-title">Upload Document</h4>
            <p className="step-card-desc">
              Officer uploads a high-resolution image of a Passport, National ID, Residence Permit, or Driver License.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">02</span>
            <h4 className="step-card-title">OCR & Analysis</h4>
            <p className="step-card-desc">
              AI engine performs image quality enhancement, text extraction, and MRZ checksum validation.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">03</span>
            <h4 className="step-card-title">Database Matching</h4>
            <p className="step-card-desc">
              Extracted fields are matched against national security registries to confirm legitimacy.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">04</span>
            <h4 className="step-card-title">Face Verification</h4>
            <p className="step-card-desc">
              Only once document integrity passes, live subject biometric capture is cross-matched against the document.
            </p>
          </div>

          <div className="workflow-step-card">
            <span className="step-num-pill">05</span>
            <h4 className="step-card-title">Decision & Risk</h4>
            <p className="step-card-desc">
              The risk engine synthesizes all forensic indicators into an actionable decision dossier for the officer.
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '36px' }}>
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

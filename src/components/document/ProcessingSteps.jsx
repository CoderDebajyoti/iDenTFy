import React from 'react';
import { Check, Loader2, Circle, ShieldAlert } from 'lucide-react';

const STAGES = [
  { id: 1, name: 'Document Received', desc: 'Validating payload checksum, file format, and resolution dimensions.' },
  { id: 2, name: 'Image Quality Check', desc: 'Evaluating sharpness, specular glare, exposure, and illumination balance.' },
  { id: 3, name: 'OCR Extraction', desc: 'Applying optical character recognition and reading MRZ code lines.' },
  { id: 4, name: 'Document Validation', desc: 'Verifying ICAO 9303 checksums, expiration validity, and field formatting.' },
  { id: 5, name: 'Database Matching', desc: 'Cross-referencing document identifiers against security records.' },
  { id: 6, name: 'Tampering Analysis', desc: 'Running digital copy-paste detection, font consistency, and metadata heuristics.' },
];

export default function ProcessingSteps({ currentStepIndex }) {
  return (
    <div className="pipeline-stages-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-brand-navy)' }}>
          Forensic Screening Stages
        </h3>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Stage {Math.min(currentStepIndex + 1, STAGES.length)} of {STAGES.length}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStepIndex;
          const isCurrent = idx === currentStepIndex;

          return (
            <div
              key={stage.id}
              className={`pipeline-stage-item ${isDone ? 'completed' : isCurrent ? 'active' : ''}`}
            >
              <div
                className={`pipeline-stage-icon ${
                  isDone ? 'done' : isCurrent ? 'current' : 'pending'
                }`}
              >
                {isDone ? (
                  <Check size={16} strokeWidth={2.5} />
                ) : isCurrent ? (
                  <Loader2 size={16} style={{ animation: 'spin 1.5s linear infinite' }} />
                ) : (
                  <Circle size={10} fill="currentColor" />
                )}
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="pipeline-stage-name">{stage.name}</span>
                  <span style={{ fontSize: '0.72rem', fontWeight: 600, color: isDone ? 'var(--color-success)' : isCurrent ? 'var(--color-brand-primary-light)' : 'var(--text-light)' }}>
                    {isDone ? 'Completed' : isCurrent ? 'In Progress...' : 'Waiting'}
                  </span>
                </div>
                <div className="pipeline-stage-desc">{stage.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

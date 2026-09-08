import React from 'react';
import { useVerification } from '../../context/VerificationContext';
import { SlidersHorizontal, CheckCircle2, AlertTriangle, XCircle, EyeOff } from 'lucide-react';

export default function InspectionBanner() {
  const { inspectionMode, setInspectionMode, activeScenario, setActiveScenario } = useVerification();

  if (!inspectionMode) {
    return (
      <button
        onClick={() => setInspectionMode(true)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 999,
          background: '#0b0f19',
          color: '#ffffff',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: 'var(--radius-full)',
          padding: '8px 16px',
          fontSize: '0.78rem',
          fontWeight: 600,
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.25)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
        title="Show Evaluation / Presentation Scenario Controls"
      >
        <SlidersHorizontal size={14} style={{ color: '#60a5fa' }} />
        <span>Scenario Controls</span>
      </button>
    );
  }

  return (
    <aside className="inspection-banner" aria-label="Evaluation simulation toolbar">
      <div className="inspection-banner-left">
        <span className="inspection-tag">Demo Sandbox</span>
        <span style={{ color: '#94a3b8', fontSize: '0.8rem', fontWeight: 500 }}>
          Simulation Scenarios:
        </span>
        <div className="scenario-pills" role="radiogroup" aria-label="Screening outcomes">
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'verified' ? 'active' : ''}`}
            onClick={() => setActiveScenario('verified')}
            role="radio"
            aria-checked={activeScenario === 'verified'}
          >
            <CheckCircle2 size={13} style={{ color: activeScenario === 'verified' ? '#ffffff' : '#10b981' }} />
            <span>01. Verified (Pass)</span>
          </button>
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'review' ? 'active' : ''}`}
            onClick={() => setActiveScenario('review')}
            role="radio"
            aria-checked={activeScenario === 'review'}
          >
            <AlertTriangle size={13} style={{ color: activeScenario === 'review' ? '#ffffff' : '#f59e0b' }} />
            <span>02. Flagged (Review)</span>
          </button>
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'failed' ? 'active' : ''}`}
            onClick={() => setActiveScenario('failed')}
            role="radio"
            aria-checked={activeScenario === 'failed'}
          >
            <XCircle size={13} style={{ color: activeScenario === 'failed' ? '#ffffff' : '#ef4444' }} />
            <span>03. Tampered (Failed)</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          type="button"
          onClick={() => setInspectionMode(false)}
          style={{
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            fontSize: '0.78rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 8px',
            borderRadius: 'var(--radius-sm)',
            transition: 'color 0.15s ease',
          }}
          title="Minimize toolbar"
        >
          <EyeOff size={13} />
          <span>Minimize</span>
        </button>
      </div>
    </aside>
  );
}

import React from 'react';
import { useVerification } from '../../context/VerificationContext';
import { SlidersHorizontal, CheckCircle, AlertTriangle, XCircle, Eye, EyeOff } from 'lucide-react';

export default function InspectionBanner() {
  const { inspectionMode, setInspectionMode, activeScenario, setActiveScenario } = useVerification();

  if (!inspectionMode) {
    return (
      <button
        onClick={() => setInspectionMode(true)}
        style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          zIndex: 999,
          background: '#0f172a',
          color: 'white',
          border: '1px solid #334155',
          borderRadius: '20px',
          padding: '6px 14px',
          fontSize: '0.78rem',
          fontWeight: 600,
          boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          cursor: 'pointer',
        }}
        title="Show Evaluator / Inspection Scenario Controls"
      >
        <SlidersHorizontal size={14} />
        <span>Inspection Toolbar</span>
      </button>
    );
  }

  return (
    <div className="inspection-banner">
      <div className="inspection-banner-left">
        <span className="inspection-tag">Evaluation / Presentation Mode</span>
        <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
          Simulate verification outcome scenarios:
        </span>
        <div className="scenario-pills">
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'verified' ? 'active' : ''}`}
            onClick={() => setActiveScenario('verified')}
          >
            <CheckCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />
            01. Verified (Pass)
          </button>
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'review' ? 'active' : ''}`}
            onClick={() => setActiveScenario('review')}
          >
            <AlertTriangle size={12} style={{ display: 'inline', marginRight: '4px' }} />
            02. Requires Review
          </button>
          <button
            type="button"
            className={`scenario-pill-btn ${activeScenario === 'failed' ? 'active' : ''}`}
            onClick={() => setActiveScenario('failed')}
          >
            <XCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />
            03. Forgery / Failed
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
            gap: '4px',
          }}
        >
          <EyeOff size={13} />
          <span>Hide</span>
        </button>
      </div>
    </div>
  );
}

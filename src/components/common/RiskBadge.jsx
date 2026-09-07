import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

export default function RiskBadge({ level }) {
  const norm = String(level || '').toLowerCase();

  if (norm === 'low') {
    return (
      <span className="risk-pill risk-low">
        <ShieldCheck size={13} />
        <span>Low Risk</span>
      </span>
    );
  }

  if (norm === 'medium') {
    return (
      <span className="risk-pill risk-medium">
        <ShieldAlert size={13} />
        <span>Medium Risk</span>
      </span>
    );
  }

  if (norm === 'high') {
    return (
      <span className="risk-pill risk-high">
        <ShieldX size={13} />
        <span>High Risk</span>
      </span>
    );
  }

  return (
    <span className="risk-pill" style={{ background: '#f1f5f9', color: '#64748b' }}>
      <span>Pending</span>
    </span>
  );
}

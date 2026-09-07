import React from 'react';
import RiskBadge from './RiskBadge';

export default function RiskMeter({ score = 15, level = 'Low' }) {
  const percentage = Math.min(Math.max(score, 0), 100);
  const normLevel = String(level || 'low').toLowerCase();

  return (
    <div className="risk-meter-container">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          Risk Assessment Index
        </span>
        <RiskBadge level={level} />
      </div>

      <div style={{ margin: '14px 0 6px', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
        <span style={{ fontSize: '2.4rem', fontWeight: 800, color: 'var(--color-brand-navy)', lineHeight: 1 }}>
          {score}
        </span>
        <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ 100</span>
      </div>

      <div className="risk-gauge-track">
        <div
          className={`risk-gauge-fill ${normLevel}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="risk-legend-row">
        <span>0 (Minimum Risk)</span>
        <span>50 (Review Threshold)</span>
        <span>100 (Critical Fraud)</span>
      </div>
    </div>
  );
}

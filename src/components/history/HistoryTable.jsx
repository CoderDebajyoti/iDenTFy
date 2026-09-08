import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, FileSearch, Calendar, RotateCcw, Plus } from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import RiskBadge from '../common/RiskBadge';
import Button from '../common/Button';

export default function HistoryTable({ records, onReset }) {
  if (!records || records.length === 0) {
    return (
      <div className="empty-state-card">
        <div className="empty-state-icon-circle">
          <FileSearch size={36} strokeWidth={1.7} />
        </div>
        <h3 className="empty-state-title">
          No Verification Records Found
        </h3>
        <p className="empty-state-desc">
          No historical screening events match your active search terms or filter criteria.
          Try clearing your filters or start a new document screening.
        </p>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
          {onReset && (
            <Button variant="secondary" size="md" icon={RotateCcw} onClick={onReset}>
              Clear Filters
            </Button>
          )}
          <Link to="/verify/document">
            <Button variant="primary" size="md" icon={Plus}>
              New Screening
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Verification ID</th>
            <th>Date & Time (UTC)</th>
            <th>Subject & Document</th>
            <th>Status</th>
            <th>Risk Level</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {records.map((rec) => (
            <tr key={rec.id}>
              <td>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: '#2563eb',
                    fontSize: '0.85rem',
                    background: '#eff6ff',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid #bfdbfe',
                  }}
                >
                  {rec.id}
                </span>
              </td>
              <td>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  <Calendar size={13} style={{ color: 'var(--text-muted)' }} />
                  <span>{rec.timestamp}</span>
                </div>
              </td>
              <td>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                    {rec.holderName}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {rec.documentType} • <span style={{ fontFamily: 'var(--font-mono)' }}>{rec.documentNumber}</span>
                  </span>
                </div>
              </td>
              <td>
                <StatusBadge status={rec.status} size="sm" />
              </td>
              <td>
                <RiskBadge level={rec.riskLevel} />
              </td>
              <td style={{ textAlign: 'right' }}>
                <Link to={`/history/${rec.id}`}>
                  <Button variant="secondary" size="sm" icon={ChevronRight}>
                    View Dossier
                  </Button>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, FileSearch, Calendar, Shield } from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import RiskBadge from '../common/RiskBadge';
import Button from '../common/Button';

export default function HistoryTable({ records }) {
  if (!records || records.length === 0) {
    return (
      <div
        className="card"
        style={{ textAlign: 'center', padding: '50px 20px', color: 'var(--text-muted)' }}
      >
        <FileSearch size={44} style={{ margin: '0 auto 14px', color: 'var(--text-light)' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--color-brand-navy)', marginBottom: '6px' }}>
          No Verification Records Found
        </h3>
        <p style={{ fontSize: '0.85rem', maxWidth: '420px', margin: '0 auto 20px' }}>
          No historical screening events match the specified search query or active filter criteria.
        </p>
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
                  }}
                >
                  {rec.id}
                </span>
              </td>
              <td>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}>
                  <Calendar size={13} style={{ color: 'var(--text-muted)' }} />
                  <span>{rec.timestamp}</span>
                </div>
              </td>
              <td>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.88rem' }}>
                    {rec.holderName}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {rec.documentType} • {rec.documentNumber}
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

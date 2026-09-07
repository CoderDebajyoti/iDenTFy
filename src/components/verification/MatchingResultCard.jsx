import React from 'react';
import { Database, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

export default function MatchingResultCard({ matchingData }) {
  if (!matchingData) return null;

  const isMatched = !String(matchingData.databaseMatch || '').toLowerCase().includes('discrep') &&
                    !String(matchingData.databaseMatch || '').toLowerCase().includes('not found') &&
                    !String(matchingData.databaseMatch || '').toLowerCase().includes('mismatch');

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-icon-box" style={{ background: '#eef2ff', color: '#4f46e5' }}>
            <Database size={18} />
          </div>
          <div>
            <h3 className="card-title">Document Matching</h3>
            <p className="card-subtitle">Database registry cross-reference & consistency</p>
          </div>
        </div>

        <span className={`badge ${isMatched ? 'badge-verified' : 'badge-review'}`}>
          {isMatched ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
          <span>{isMatched ? 'Match Confirmed' : 'Discrepancy'}</span>
        </span>
      </div>

      <div className="forensic-field-list">
        <div className="forensic-field-item">
          <span className="field-label">Database Match</span>
          <span className="field-value" style={{ color: isMatched ? 'var(--color-success)' : 'var(--color-warning)' }}>
            {matchingData.databaseMatch || 'Pending Lookup'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Field Match</span>
          <span className="field-value">
            {matchingData.fieldMatch || '—'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Name Similarity Score</span>
          <span className="field-value">
            {matchingData.nameSimilarity || '—'}
          </span>
        </div>

        <div className="forensic-field-item">
          <span className="field-label">Document Number Match</span>
          <span className="field-value">
            {matchingData.documentNumberMatch || '—'}
          </span>
        </div>
      </div>
    </div>
  );
}

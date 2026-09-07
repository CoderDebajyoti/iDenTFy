import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, Loader2, Lock } from 'lucide-react';

export default function StatusBadge({ status, size = 'default' }) {
  const norm = String(status || '').toLowerCase();

  if (norm.includes('verif') && !norm.includes('not') && !norm.includes('fail')) {
    return (
      <span className={`badge badge-verified ${size === 'sm' ? 'btn-sm' : ''}`}>
        <CheckCircle2 size={13} />
        <span>Verified</span>
      </span>
    );
  }

  if (norm.includes('review')) {
    return (
      <span className={`badge badge-review ${size === 'sm' ? 'btn-sm' : ''}`}>
        <AlertTriangle size={13} />
        <span>Requires Review</span>
      </span>
    );
  }

  if (norm.includes('fail') || norm.includes('not_verif') || norm.includes('not verif') || norm.includes('error')) {
    return (
      <span className={`badge badge-failed ${size === 'sm' ? 'btn-sm' : ''}`}>
        <XCircle size={13} />
        <span>{norm.includes('error') ? 'Error' : 'Not Verified'}</span>
      </span>
    );
  }

  if (norm.includes('process') || norm.includes('analyz')) {
    return (
      <span className={`badge badge-processing ${size === 'sm' ? 'btn-sm' : ''}`}>
        <Loader2 size={13} className="spin-icon" />
        <span>Processing</span>
      </span>
    );
  }

  if (norm.includes('lock')) {
    return (
      <span className={`badge badge-pending ${size === 'sm' ? 'btn-sm' : ''}`}>
        <Lock size={13} />
        <span>Locked</span>
      </span>
    );
  }

  return (
    <span className={`badge badge-pending ${size === 'sm' ? 'btn-sm' : ''}`}>
      <Clock size={13} />
      <span>{status || 'Pending'}</span>
    </span>
  );
}

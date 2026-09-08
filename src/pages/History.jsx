import React, { useState, useEffect, useMemo } from 'react';
import { getVerificationHistory } from '../services/api';
import HistoryFilterBar from '../components/history/HistoryFilterBar';
import HistoryTable from '../components/history/HistoryTable';
import { Download, RefreshCw, AlertCircle } from 'lucide-react';
import Button from '../components/common/Button';

export default function History() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getVerificationHistory();
      setRecords(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || 'Verification service unavailable: Unable to query database.');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredRecords = useMemo(() => {
    return records.filter((rec) => {
      // Search matching ID, Holder Name, Document Number
      const q = searchQuery.toLowerCase().trim();
      const holder = (rec.holderName || rec.holder_name || '').toLowerCase();
      const docNum = (rec.documentNumber || rec.document_number || '').toLowerCase();
      const recId = (rec.id || '').toLowerCase();

      const matchSearch =
        !q ||
        recId.includes(q) ||
        holder.includes(q) ||
        docNum.includes(q);

      // Doc type matching
      const docType = (rec.documentType || rec.document_type || '').toLowerCase();
      const matchDocType = docTypeFilter === 'all' || docType.includes(docTypeFilter.toLowerCase());

      // Status matching
      const status = (rec.status || '').toLowerCase();
      const matchStatus = statusFilter === 'all' || status.includes(statusFilter.toLowerCase());

      // Risk level matching
      const risk = (rec.riskLevel || rec.risk_level || '').toLowerCase();
      const matchRisk = riskFilter === 'all' || risk.includes(riskFilter.toLowerCase());

      return matchSearch && matchDocType && matchStatus && matchRisk;
    });
  }, [records, searchQuery, docTypeFilter, statusFilter, riskFilter]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setDocTypeFilter('all');
    setStatusFilter('all');
    setRiskFilter('all');
  };

  const handleExportCSV = () => {
    if (filteredRecords.length === 0) return;
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Verification ID,Date Time,Holder Name,Document Type,Document Number,Status,Risk Level']
        .concat(
          filteredRecords.map(
            (r) =>
              `"${r.id}","${r.timestamp}","${r.holderName || r.holder_name}","${r.documentType || r.document_type}","${r.documentNumber || r.document_number}","${r.status}","${r.riskLevel || r.risk_level}"`
          )
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `identfy_verifications_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Verification Audit History</h1>
            <p className="page-subtitle">
              Comprehensive historical log of screened identity documents, optical forensics, and biometric evaluations.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <Button variant="secondary" size="sm" icon={RefreshCw} loading={loading} onClick={loadData}>
              Refresh
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={Download}
              onClick={handleExportCSV}
              disabled={filteredRecords.length === 0}
            >
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Backend Error Banner */}
      {error && (
        <div
          style={{
            marginBottom: '20px',
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.85rem',
            color: '#991b1b',
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <div style={{ flex: 1 }}>
            <strong>Database Connection Error:</strong> {error}
          </div>
          <Button variant="secondary" size="sm" onClick={loadData}>
            Retry
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <HistoryFilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        docTypeFilter={docTypeFilter}
        onDocTypeChange={setDocTypeFilter}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
        riskFilter={riskFilter}
        onRiskChange={setRiskFilter}
        onReset={handleResetFilters}
      />

      {/* Records Table */}
      <HistoryTable
        records={filteredRecords}
        isLoading={loading}
        onReset={handleResetFilters}
      />
    </div>
  );
}

import React, { useState, useEffect, useMemo } from 'react';
import { getVerificationHistory } from '../services/api';
import HistoryFilterBar from '../components/history/HistoryFilterBar';
import HistoryTable from '../components/history/HistoryTable';
import { History as HistoryIcon, Download, ShieldCheck } from 'lucide-react';
import Button from '../components/common/Button';

export default function History() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const data = await getVerificationHistory();
      setRecords(data);
      setLoading(false);
    }
    loadData();
  }, []);

  const filteredRecords = useMemo(() => {
    return records.filter((rec) => {
      // Search matching ID, Holder Name, Document Number
      const q = searchQuery.toLowerCase().trim();
      const matchSearch =
        !q ||
        rec.id.toLowerCase().includes(q) ||
        rec.holderName.toLowerCase().includes(q) ||
        rec.documentNumber.toLowerCase().includes(q);

      // Doc type matching
      const matchDocType = docTypeFilter === 'all' || rec.documentType === docTypeFilter;

      // Status matching
      const matchStatus = statusFilter === 'all' || rec.status === statusFilter;

      // Risk level matching
      const matchRisk = riskFilter === 'all' || rec.riskLevel === riskFilter;

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
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Verification ID,Date Time,Holder Name,Document Type,Document Number,Status,Risk Level']
        .concat(
          filteredRecords.map(
            (r) =>
              `"${r.id}","${r.timestamp}","${r.holderName}","${r.documentType}","${r.documentNumber}","${r.status}","${r.riskLevel}"`
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
            <Button variant="secondary" size="sm" icon={Download} onClick={handleExportCSV}>
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Note: Mock dataset disclaimer */}
      <div
        style={{
          marginBottom: '20px',
          padding: '10px 16px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: '#eff6ff',
          border: '1px solid #bfdbfe',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '0.8rem',
          color: '#1d4ed8',
        }}
      >
        <ShieldCheck size={16} />
        <span>
          <strong>UI Development Notice:</strong> Showing audit history records for preview. When connected to FastAPI, this page live-syncs with the central verification database.
        </span>
      </div>

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
      <HistoryTable records={filteredRecords} />
    </div>
  );
}

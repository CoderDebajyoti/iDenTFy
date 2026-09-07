import React from 'react';
import { Search, Filter, RotateCcw } from 'lucide-react';
import Button from '../common/Button';

export default function HistoryFilterBar({
  searchQuery,
  onSearchChange,
  docTypeFilter,
  onDocTypeChange,
  statusFilter,
  onStatusChange,
  riskFilter,
  onRiskChange,
  onReset,
}) {
  return (
    <div className="filter-bar">
      <div className="search-input-wrapper">
        <Search size={16} className="search-input-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Search by Verification ID, Holder Name, Document #..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <select
        className="filter-select"
        value={docTypeFilter}
        onChange={(e) => onDocTypeChange(e.target.value)}
        aria-label="Filter by Document Type"
      >
        <option value="all">All Document Types</option>
        <option value="Passport">Passport</option>
        <option value="Identity Card">Identity Card</option>
        <option value="Residence Permit">Residence Permit</option>
        <option value="Driver License">Driver License</option>
      </select>

      <select
        className="filter-select"
        value={statusFilter}
        onChange={(e) => onStatusChange(e.target.value)}
        aria-label="Filter by Status"
      >
        <option value="all">All Statuses</option>
        <option value="Verified">Verified</option>
        <option value="Requires Review">Requires Review</option>
        <option value="Verification Failed">Verification Failed</option>
      </select>

      <select
        className="filter-select"
        value={riskFilter}
        onChange={(e) => onRiskChange(e.target.value)}
        aria-label="Filter by Risk Level"
      >
        <option value="all">All Risk Tiers</option>
        <option value="Low">Low Risk</option>
        <option value="Medium">Medium Risk</option>
        <option value="High">High Risk</option>
      </select>

      {(searchQuery || docTypeFilter !== 'all' || statusFilter !== 'all' || riskFilter !== 'all') && (
        <Button variant="ghost" size="sm" icon={RotateCcw} onClick={onReset}>
          Reset Filters
        </Button>
      )}
    </div>
  );
}

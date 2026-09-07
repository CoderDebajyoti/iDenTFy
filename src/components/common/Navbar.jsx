import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Plus, ShieldAlert, UserCheck, ChevronRight } from 'lucide-react';
import Button from './Button';

export default function Navbar({ onToggleSidebar }) {
  const location = useLocation();

  // Breadcrumb generator
  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/verify/document/result')) return 'Document Result';
    if (path.startsWith('/verify/document/processing')) return 'Processing Analysis';
    if (path.startsWith('/verify/document')) return 'Document Verification';
    if (path.startsWith('/verify/face')) return 'Face Verification';
    if (path.startsWith('/verify/final')) return 'Final Verification Result';
    if (path.startsWith('/history/')) return 'Verification Dossier';
    if (path.startsWith('/history')) return 'Verification History';
    if (path.startsWith('/settings')) return 'System Settings';
    return 'Console';
  };

  return (
    <header className="top-header">
      <div className="top-header-left">
        <button
          type="button"
          className="mobile-menu-trigger"
          onClick={onToggleSidebar}
          aria-label="Toggle navigation menu"
        >
          <Menu size={22} />
        </button>

        <div className="header-breadcrumbs">
          <span style={{ color: 'var(--text-muted)' }}>iDenTFy</span>
          <ChevronRight size={14} />
          <span className="crumb-active">{getBreadcrumb()}</span>
        </div>
      </div>

      <div className="top-header-right">
        {location.pathname !== '/verify/document' && (
          <Link to="/verify/document">
            <Button size="sm" variant="primary" icon={Plus}>
              New Screening
            </Button>
          </Link>
        )}

        <div className="header-officer-badge">
          <div className="officer-avatar">MHA</div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 600, fontSize: '0.78rem', color: 'var(--text-primary)' }}>
              Immigration Officer • BOI
            </span>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              Ministry of Home Affairs, Govt. of India
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

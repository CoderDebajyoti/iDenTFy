import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Plus, ChevronRight, Shield } from 'lucide-react';
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
          aria-label="Toggle navigation drawer"
        >
          <Menu size={20} />
        </button>

        <nav aria-label="Breadcrumb" className="header-breadcrumbs">
          <Link to="/" className="breadcrumb-root">
            <Shield size={14} style={{ color: '#2563eb' }} />
            <span>iDenTFy</span>
          </Link>
          <ChevronRight size={13} style={{ color: '#94a3b8' }} />
          <span className="crumb-active">{getBreadcrumb()}</span>
        </nav>
      </div>

      <div className="top-header-right">
        {location.pathname !== '/verify/document' && (
          <Link to="/verify/document">
            <Button size="sm" variant="primary" icon={Plus}>
              New Screening
            </Button>
          </Link>
        )}

        <div className="header-officer-badge" title="Authenticated Security Officer Profile">
          <div className="officer-avatar">MHA</div>
          <div className="officer-info">
            <span className="officer-name">
              Immigration Officer • BOI
            </span>
            <span className="officer-role">
              Ministry of Home Affairs
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

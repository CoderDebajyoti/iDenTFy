import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Shield,
  FileCheck2,
  History,
  Settings,
  LayoutDashboard,
  Server,
  ChevronRight
} from 'lucide-react';
import { checkSystemHealth } from '../../services/api';

export default function Sidebar({ isOpen, onClose }) {
  const [healthStatus, setHealthStatus] = useState({ online: false, checking: true });

  useEffect(() => {
    let isMounted = true;
    async function probe() {
      const res = await checkSystemHealth();
      if (isMounted) {
        setHealthStatus({ online: res.online, checking: false });
      }
    }
    probe();
    const interval = setInterval(probe, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <aside className={`app-sidebar ${isOpen ? 'mobile-open' : ''}`}>
      {/* Sidebar Header / Logo */}
      <div className="app-sidebar-header">
        <div className="brand-logo-icon">
          <Shield size={22} strokeWidth={2.4} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="brand-title">
            <span>iDenTFy</span>
            <span className="brand-badge">MHA • SIH</span>
          </div>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
            Ministry of Home Affairs, GoI
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Core Operations</div>

        <NavLink
          to="/"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
          end
        >
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/verify/document"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <FileCheck2 size={18} />
          <span>New Verification</span>
          <span className="nav-badge-pill">Workflow</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <History size={18} />
          <span>History & Audit</span>
        </NavLink>

        <div className="nav-section-title" style={{ marginTop: '16px' }}>System Control</div>

        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <Settings size={18} />
          <span>Settings & API</span>
        </NavLink>
      </nav>

      {/* Subtle Bottom System Status */}
      <div className="sidebar-footer">
        <div className="system-status-indicator">
          <span className={`status-dot ${healthStatus.online ? 'online' : 'offline'}`} />
          <div className="status-info">
            <span className="status-label">
              {healthStatus.online ? 'FastAPI Connected' : 'Standalone / Preview'}
            </span>
            <span className="status-sublabel">
              {healthStatus.online ? 'API v1 active' : 'Simulated OCR pipeline'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

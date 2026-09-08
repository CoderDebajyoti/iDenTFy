import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  Shield,
  FileCheck2,
  History,
  Settings,
  LayoutDashboard,
  X,
  Radio,
  Cpu
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
    <aside
      className={`app-sidebar ${isOpen ? 'mobile-open' : ''}`}
      aria-label="Sidebar navigation"
    >
      {/* Sidebar Header / Logo */}
      <div className="app-sidebar-header">
        <Link to="/" className="brand-link-wrapper" onClick={onClose}>
          <div className="brand-logo-icon">
            <Shield size={20} strokeWidth={2.4} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="brand-title">
              <span>iDenTFy</span>
              <span className="brand-badge">SaaS</span>
            </div>
            <span style={{ fontSize: '0.67rem', color: '#64748b', letterSpacing: '0.04em' }}>
              Identity & Forensic Intel
            </span>
          </div>
        </Link>

        <button
          type="button"
          className="sidebar-close-btn"
          onClick={onClose}
          aria-label="Close sidebar navigation"
        >
          <X size={18} />
        </button>
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
          <LayoutDashboard size={18} className="nav-icon" />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/verify/document"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <FileCheck2 size={18} className="nav-icon" />
          <span>New Screening</span>
          <span className="nav-badge-pill">Live</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <History size={18} className="nav-icon" />
          <span>Audit History</span>
        </NavLink>

        <div className="nav-section-title" style={{ marginTop: '16px' }}>System Control</div>

        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
          onClick={onClose}
        >
          <Settings size={18} className="nav-icon" />
          <span>Settings & API</span>
        </NavLink>
      </nav>

      {/* Bottom System Status */}
      <div className="sidebar-footer">
        <div className="system-status-indicator" title={healthStatus.online ? 'FastAPI Service Connected' : 'Simulated OCR & Forensics Mode'}>
          <div className="status-dot-wrapper">
            <span className={`status-dot-pulse ${healthStatus.online ? 'online' : 'offline'}`} />
            <span className={`status-dot ${healthStatus.online ? 'online' : 'offline'}`} />
          </div>
          <div className="status-info">
            <span className="status-label">
              {healthStatus.online ? 'Engine Active' : 'Sandbox Preview'}
            </span>
            <span className="status-sublabel">
              {healthStatus.online ? 'FastAPI v1 Connected' : 'Local Mock Pipeline'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

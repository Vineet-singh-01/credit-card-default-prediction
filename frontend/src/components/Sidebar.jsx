import { NavLink } from 'react-router-dom';
import { Activity, BarChart3, BookOpen, BrainCircuit, ChevronLeft, Clock3, Gauge, LayoutDashboard, ShieldCheck, Sparkles, X } from 'lucide-react';

const primaryLinks = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/prediction', label: 'Risk assessment', icon: BrainCircuit },
  { to: '/results', label: 'Latest result', icon: Gauge },
  { to: '/insights', label: 'Data insights', icon: BarChart3 },
  { to: '/performance', label: 'Model performance', icon: Activity },
  { to: '/history', label: 'Prediction history', icon: Clock3 },
];

export default function Sidebar({ open, onClose, collapsed, onCollapse }) {
  return (
    <>
      {open && <button className="sidebar-scrim" aria-label="Close navigation" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'sidebar-open' : ''} ${collapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="brand-row">
          <div className="brand-mark"><ShieldCheck size={21} /></div>
          {!collapsed && <div className="brand-copy"><strong>CreditRisk</strong><span>ANALYTICS PLATFORM</span></div>}
          <button className="icon-button sidebar-close" onClick={onClose} aria-label="Close navigation"><X size={18} /></button>
        </div>
        <div className="workspace-chip"><span className="online-dot" />{!collapsed && 'ACADEMIC WORKSPACE'}</div>
        <nav className="nav-list" aria-label="Main navigation">
          <div className="nav-caption">WORKSPACE</div>
          {primaryLinks.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} onClick={onClose} title={collapsed ? label : undefined} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Icon size={18} strokeWidth={1.8} /><span>{label}</span>
              {label === 'Latest result' && <span className="nav-live-dot" />}
            </NavLink>
          ))}
          <div className="nav-caption nav-caption-spaced">PROJECT</div>
          <NavLink to="/about" onClick={onClose} title={collapsed ? 'About the project' : undefined} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <BookOpen size={18} strokeWidth={1.8} /><span>About the project</span>
          </NavLink>
        </nav>
        <div className="sidebar-bottom">
          {!collapsed && <div className="sidebar-note"><Sparkles size={15} /><div><strong>Decision support</strong><span>Human review always required.</span></div></div>}
          <button className="collapse-button" onClick={onCollapse} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
            <ChevronLeft size={17} className={collapsed ? 'rotate-180' : ''} />{!collapsed && 'Collapse menu'}
          </button>
          {!collapsed && <div className="sidebar-version">CREDITRISK ANALYTICS <span>v1.0.0</span></div>}
        </div>
      </aside>
    </>
  );
}

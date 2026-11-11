import { motion } from 'motion/react';
import { AlertCircle, ArrowUpRight, LoaderCircle, RefreshCw } from 'lucide-react';

export function PageHeading({ eyebrow, title, description, action }) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action && <div className="page-heading-action">{action}</div>}
    </div>
  );
}

export function MetricCard({ label, value, detail, icon: Icon, tone = 'teal', footnote }) {
  return (
    <motion.section className="metric-card card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
      <div className="metric-card-top">
        <span>{label}</span>
        {Icon && <span className={`metric-icon ${tone}`}><Icon size={18} /></span>}
      </div>
      <div className="metric-value">{value ?? '—'}</div>
      {detail && <div className="metric-detail">{detail}</div>}
      {footnote && <div className="metric-footnote">{footnote}</div>}
    </motion.section>
  );
}

export function Panel({ title, subtitle, action, children, className = '' }) {
  return (
    <section className={`panel card ${className}`}>
      {(title || action) && <div className="panel-heading"><div>{title && <h2>{title}</h2>}{subtitle && <p>{subtitle}</p>}</div>{action}</div>}
      {children}
    </section>
  );
}

export function LoadingState({ label = 'Loading project data…' }) {
  return <div className="state-card"><LoaderCircle className="spin" size={24} /><span>{label}</span></div>;
}

export function ErrorState({ message, onRetry }) {
  return <div className="state-card error-state"><AlertCircle size={22} /><div><strong>We couldn't load this section.</strong><p>{message}</p>{onRetry && <button className="button button-secondary button-small" onClick={onRetry}><RefreshCw size={14} /> Try again</button>}</div></div>;
}

export function EmptyState({ title, description, action }) {
  return <div className="empty-state"><div className="empty-icon"><ArrowUpRight size={22} /></div><h3>{title}</h3><p>{description}</p>{action}</div>;
}

export function SectionLabel({ children, right }) {
  return <div className="section-label"><span>{children}</span>{right}</div>;
}

export function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(value));
}

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

export function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

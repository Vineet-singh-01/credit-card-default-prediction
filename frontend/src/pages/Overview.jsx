import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight, ArrowUpRight, BrainCircuit, ClipboardList, Database, Gauge, ShieldCheck, Sparkles, Target, Users } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../services/api';
import { ErrorState, LoadingState, MetricCard, PageHeading, Panel, EmptyState, formatDate, formatNumber, formatPercent } from '../components/UI';

const CHART_COLORS = ['#13A89E', '#DDE6ED'];

export default function Overview() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const load = useCallback(() => {
    setError('');
    api.overview().then(setData).catch((err) => setError(err.message));
  }, []);
  useEffect(() => { load(); }, [load]);

  if (error) return <><PageHeading eyebrow="PORTFOLIO INTELLIGENCE" title="Good to see you." description="Your credit-risk analytics workspace at a glance." /><ErrorState message={error} onRetry={load} /></>;
  if (!data) return <LoadingState />;

  const metrics = data.metrics || {};
  const dataset = data.dataset || {};
  const distribution = [
    { name: 'No default', value: Number(dataset.no_default_count || 0) },
    { name: 'Default', value: Number(dataset.default_count || 0) },
  ];
  const history = data.recent_predictions || [];
  const recentTrend = [...history].reverse().map((item, index) => ({ label: `#${item.id}`, score: Number(item.score || 0) * 100, index }));

  return (
    <>
      <PageHeading eyebrow="PORTFOLIO INTELLIGENCE" title="Good to see you." description="A clear view of portfolio patterns, model quality, and recent assessment activity."
        action={<Link to="/prediction" className="button button-primary"><BrainCircuit size={16} /> Run an assessment</Link>} />
      <section className="welcome-banner">
        <div className="welcome-copy"><div className="banner-kicker"><Sparkles size={14} /> MODEL WORKSPACE</div><h2>Credit decisions start with better signals.</h2><p>Explore historical credit behaviour and use the saved model as one input to informed, qualified human review.</p><div className="banner-actions"><Link to="/insights" className="button button-white">Explore insights <ArrowRight size={15} /></Link><Link to="/about" className="banner-link">How this works <ArrowUpRight size={15} /></Link></div></div>
        <div className="banner-art" aria-hidden="true"><div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/><div className="art-core"><ShieldCheck size={43}/></div><span className="art-tag tag-a">MODEL SIGNAL</span><span className="art-tag tag-b">HUMAN REVIEW</span></div>
      </section>

      <div className="section-label"><span>PROJECT SNAPSHOT</span><span className="muted-inline">Source: UCI Taiwan credit-card dataset · 2005</span></div>
      <div className="metric-grid metric-grid-four">
        <MetricCard label="Customer records" value={formatNumber(dataset.rows)} detail={`${formatNumber(dataset.predictors)} predictor variables`} icon={Users} tone="blue" />
        <MetricCard label="Observed default rate" value={dataset.observed_default_rate == null ? '—' : `${Number(dataset.observed_default_rate).toFixed(2)}%`} detail="Historical dataset share" icon={Target} tone="amber" />
        <MetricCard label="Held-out test accuracy" value={formatPercent(metrics.accuracy)} detail="Correct classifications at 0.50" icon={Gauge} tone="teal" />
        <MetricCard label="Predictions performed" value={formatNumber(data.predictions_performed)} detail="Saved from this API instance" icon={Activity} tone="violet" />
      </div>

      <div className="dashboard-grid dashboard-grid-main">
        <Panel title="Dataset outcome mix" subtitle="Observed target distribution across all audited records." action={<Link className="text-link" to="/insights">Full insights <ArrowRight size={14}/></Link>}>
          <div className="donut-layout">
            <div className="donut-wrap"><ResponsiveContainer width="100%" height={210}><PieChart><Pie data={distribution} dataKey="value" nameKey="name" innerRadius={63} outerRadius={88} paddingAngle={4} stroke="none">{distribution.map((entry, i) => <Cell key={entry.name} fill={CHART_COLORS[i]} />)}</Pie><Tooltip formatter={(value) => formatNumber(value)} /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{formatNumber(dataset.rows)}</strong><span>records</span></div></div>
            <div className="legend-list">{distribution.map((entry, i) => <div className="legend-item" key={entry.name}><span className="legend-dot" style={{ background: CHART_COLORS[i] }}/><div><strong>{entry.name}</strong><span>{formatNumber(entry.value)} records</span></div><b>{dataset.rows ? `${(entry.value / dataset.rows * 100).toFixed(2)}%` : '—'}</b></div>)}</div>
          </div>
          <div className="insight-callout"><div className="callout-icon"><Database size={17}/></div><p>The observed default class represents <strong>{dataset.observed_default_rate == null ? '—' : `${Number(dataset.observed_default_rate).toFixed(2)}%`}</strong> of this historical dataset. Accuracy should therefore be read alongside default precision and recall.</p></div>
        </Panel>
        <Panel title="Model quality" subtitle={`${data.model_name || 'Saved model'} · held-out test set`} action={<Link className="text-link" to="/performance">Model details <ArrowRight size={14}/></Link>}>
          <div className="quality-list">
            {[['Default precision', metrics.precision_default, 'How often a default flag was correct'], ['Default recall', metrics.recall_default, 'How many actual defaults were identified'], ['Default F1-score', metrics.f1_default, 'Balance between precision and recall']].map(([label, value, helper]) => <div className="quality-item" key={label}><div className="quality-line"><strong>{label}</strong><b>{formatPercent(value)}</b></div><div className="meter-track"><span style={{ width: `${Math.max(0, Math.min(100, Number(value || 0) * 100))}%` }}/></div><small>{helper}</small></div>)}
          </div>
          <div className="quality-foot"><span><span className="status-dot"/> Metrics loaded from test report</span><span>ROC-AUC <b>{metrics.roc_auc == null ? '—' : Number(metrics.roc_auc).toFixed(3)}</b></span></div>
        </Panel>
      </div>

      <div className="dashboard-grid dashboard-grid-bottom">
        <Panel title="Recent assessments" subtitle="Real prediction requests saved by this application." action={<Link className="text-link" to="/history">View history <ArrowRight size={14}/></Link>}>
          {history.length ? <div className="activity-list">{history.map((item) => <Link to={`/results/${item.id}`} className="activity-row" key={item.id}><div className={`activity-avatar ${item.technical_prediction ? 'avatar-high' : 'avatar-low'}`}><ClipboardList size={17}/></div><div className="activity-main"><strong>Assessment #{item.id}</strong><span>{formatDate(item.created_at)}</span></div><div className="activity-result"><b>{formatPercent(item.score)}</b><span>{item.category}</span></div><ArrowUpRight size={16} className="activity-arrow"/></Link>)}</div> : <EmptyState title="No assessments yet" description="Your completed model assessments will appear here." action={<Link to="/prediction" className="button button-primary button-small">Create first assessment</Link>} />}
        </Panel>
        <Panel title="Score activity" subtitle="Recent uncalibrated model scores from saved assessments.">
          {recentTrend.length ? <ResponsiveContainer width="100%" height={210}><AreaChart data={recentTrend} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}><defs><linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#13A89E" stopOpacity={0.22}/><stop offset="100%" stopColor="#13A89E" stopOpacity={0.01}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--chart-grid)"/><XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 11 }}/><YAxis domain={[0,100]} tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={(value) => `${value}%`}/><Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Model score']}/><Area type="monotone" dataKey="score" stroke="#13A89E" strokeWidth={2.4} fill="url(#scoreFill)" activeDot={{ r: 5 }}/></AreaChart></ResponsiveContainer> : <EmptyState title="Waiting for your first score" description="Run a customer assessment to populate this chart." />}
          <p className="chart-disclaimer">Scores are not separately calibrated probabilities and should not be compared as customer creditworthiness grades.</p>
        </Panel>
      </div>
      <div className="disclaimer-strip"><ShieldCheck size={17}/><span><strong>Responsible use:</strong> This prototype uses Taiwanese customer data from 2005 and has not been validated for current Indian portfolios. Predictions support human review only.</span></div>
    </>
  );
}

import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { AlertTriangle, ArrowLeft, ArrowRight, CheckCircle2, Download, Gauge, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import { RadialBar, RadialBarChart, ResponsiveContainer, Tooltip } from 'recharts';
import { api, downloadCsv } from '../services/api';
import { ErrorState, LoadingState, MetricCard, PageHeading, Panel, EmptyState, formatDate, formatPercent } from '../components/UI';

const categoryStyle = {
  'Lower score band': 'tone-low', 'Watchlist score band': 'tone-watch',
  'Elevated score band': 'tone-elevated', 'High review-priority band': 'tone-high',
};
const guidance = {
  'Lower score band': 'Routine monitoring', 'Watchlist score band': 'Routine account review',
  'Elevated score band': 'Prioritised manual review', 'High review-priority band': 'Timely authorised review',
};

function InputSummary({ inputs }) {
  if (!inputs) return null;
  const values = [
    ['Credit limit', `NT$ ${Number(inputs.LIMIT_BAL || 0).toLocaleString('en-IN')}`],
    ['Age', `${inputs.AGE} years`], ['Gender', ({ 1: 'Male', 2: 'Female' })[inputs.SEX] || 'Unknown'],
    ['Education', ({ 0: 'Not reported / unknown', 1: 'Graduate school', 2: 'University', 3: 'High school', 4: 'Other', 5: 'Unknown', 6: 'Unknown' })[inputs.EDUCATION] || 'Unknown'],
    ['Marital status', ({ 0: 'Not reported / unknown', 1: 'Married', 2: 'Single / unmarried', 3: 'Other' })[inputs.MARRIAGE] || 'Unknown'],
    ['Latest repayment status', ({ '-2': 'No consumption recorded', '-1': 'Paid duly / on time', 0: 'Revolving credit', 1: '1 month late', 2: '2 months late', 3: '3 months late', 4: '4 months late', 5: '5 months late', 6: '6 months late', 7: '7 months late', 8: '8 months late' })[inputs.PAY_0] || 'Unknown'],
  ];
  return <div className="summary-grid">{values.map(([label, value]) => <div className="summary-cell" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>;
}

export default function Results() {
  const { id } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(location.state?.result || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedThreshold, setSelectedThreshold] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setError('');

    if (id && location.state?.result && String(location.state.result.id) === id) {
      setResult(location.state.result);
      setLoading(false);
      return () => { cancelled = true; };
    }

    setLoading(true);
    const loadResult = id
      ? api.prediction(id)
      : location.state?.result
        ? Promise.resolve(location.state.result)
        : api.history(1).then((history) => {
            const latest = history.items?.[0];
            return latest ? api.prediction(latest.id) : null;
          });

    loadResult
      .then((value) => { if (!cancelled) setResult(value); })
      .catch((err) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [id, location.state]);

  const score = Number(result?.score || 0);
  const threshold = Number(result?.technical_threshold ?? result?.threshold ?? 0.5);
  const category = result?.category || 'Not available';
  const thresholdValue = selectedThreshold ?? threshold;
  const isFlagged = score >= thresholdValue;
  const diagnostics = result?.diagnostics || {};
  const csvRow = useMemo(() => result ? [{
    prediction_id: result.id, created_at: result.created_at, uncalibrated_model_score: score,
    illustrative_category: category, technical_threshold: threshold,
    technical_prediction: Boolean(result.technical_prediction),
    ...Object.fromEntries(Object.entries(result.inputs || {}).map(([key, value]) => [`input_${key}`, value])),
  }] : [], [result, score, category, threshold]);

  if (loading) return <LoadingState label="Loading saved assessment…"/>;
  if (error) return <><PageHeading eyebrow="ASSESSMENT OUTPUT" title="Result unavailable" description="We could not retrieve this assessment from local history."/><ErrorState message={error} onRetry={() => { setError(''); setLoading(true); api.prediction(id).then(setResult).catch((err) => setError(err.message)).finally(() => setLoading(false)); }}/></>;
  if (!result) return <><PageHeading eyebrow="ASSESSMENT OUTPUT" title="Assessment results" description="Results appear here after a customer profile has been submitted to the model."/><EmptyState title="No result selected" description="Start a customer assessment to see the saved model output and profile diagnostics." action={<Link to="/prediction" className="button button-primary">Start assessment <ArrowRight size={15}/></Link>}/></>;

  const gaugeData = [{ name: 'Model score', value: score * 100, fill: '#12A89E' }];
  return (
    <>
      <PageHeading eyebrow="ASSESSMENT OUTPUT" title={`Assessment #${result.id}`} description={`Generated ${formatDate(result.created_at)} · ${result.model_name || 'Saved Random Forest model'}`} action={<button className="button button-secondary" onClick={() => downloadCsv(`credit-risk-assessment-${result.id}.csv`, csvRow)}><Download size={16}/> Download report</button>}/>
      <div className="assessment-notice"><ShieldCheck size={18}/><div><strong>Human review required</strong><span>This score is uncalibrated. It is a model output for academic decision-support demonstration, not a verified probability or an automatic credit decision.</span></div></div>
      <div className="result-hero-grid">
        <Panel title="Model score" subtitle="Uncalibrated output for the default class.">
          <div className="result-gauge-layout"><div className="result-gauge"><ResponsiveContainer width="100%" height={220}><RadialBarChart innerRadius="72%" outerRadius="100%" data={gaugeData} startAngle={210} endAngle={-30} barSize={15}><RadialBar dataKey="value" cornerRadius={10} background={{ fill: 'var(--surface-soft)' }}/><Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Model score']}/></RadialBarChart></ResponsiveContainer><div className="result-gauge-value"><strong>{formatPercent(score)}</strong><span>model score</span></div></div><div className="gauge-explainer"><div className={`risk-pill ${categoryStyle[category] || ''}`}>{category}</div><h3>{guidance[category] || 'Qualified review'}</h3><p>The score is shown on a 0–100 display scale. It has not been separately calibrated and should not be interpreted as an actual default probability.</p><div className="score-scale"><span>0%</span><div className="score-scale-track"><i style={{ left: `${score * 100}%` }}/></div><span>100%</span></div></div></div>
        </Panel>
        <Panel title="Technical classification" subtitle="A threshold comparison, separate from the illustrative score category.">
          <div className={`classification-box ${isFlagged ? 'classification-flag' : 'classification-clear'}`}><div className="classification-icon">{isFlagged ? <AlertTriangle size={23}/> : <CheckCircle2 size={23}/>}</div><div><span>At selected cutoff</span><strong>{isFlagged ? 'Default flag' : 'No default flag'}</strong><small>{isFlagged ? 'Score is at or above the selected threshold.' : 'Score is below the selected threshold.'}</small></div></div>
          <div className="threshold-control"><div className="threshold-heading"><label htmlFor="threshold">Explore a technical threshold</label><strong>{(thresholdValue * 100).toFixed(0)}%</strong></div><input id="threshold" type="range" min="0.05" max="0.95" step="0.01" value={thresholdValue} onChange={(event) => setSelectedThreshold(Number(event.target.value))}/><div className="threshold-scale"><span>5%</span><span>50%</span><span>95%</span></div><p>Default model cutoff: {(threshold * 100).toFixed(0)}%. This slider changes only the displayed binary flag; it does not alter or retrain the model.</p><button className="button button-ghost button-small" onClick={() => setSelectedThreshold(null)}><SlidersHorizontal size={14}/> Reset to model cutoff</button></div>
        </Panel>
      </div>

      <div className="section-label"><span>PROFILE INDICATORS</span><span className="muted-inline">Descriptive calculations from submitted inputs</span></div>
      <div className="metric-grid metric-grid-four">
        <MetricCard label="Months with delay code" value={`${diagnostics.months_with_delay_code ?? '—'} / ${diagnostics.months_reviewed ?? 6}`} detail="Across six historical repayment fields" icon={Gauge} tone="amber" />
        <MetricCard label="Latest repayment status" value={diagnostics.latest_repayment_status || '—'} detail="PAY_0 source field" icon={CheckCircle2} tone="teal" />
        <MetricCard label="Bill / credit limit" value={diagnostics.credit_limit_utilisation_pct == null ? 'Not available' : `${diagnostics.credit_limit_utilisation_pct}%`} detail="Latest bill divided by credit limit" icon={ArrowRight} tone="blue" />
        <MetricCard label="Payment / latest bill" value={diagnostics.latest_payment_to_bill_pct == null ? 'Not available' : `${diagnostics.latest_payment_to_bill_pct}%`} detail="Latest payment divided by bill" icon={Gauge} tone="violet" />
      </div>

      <Panel title="Submitted customer profile" subtitle="The values sent to the saved model. Demographic values are shown as labels, not numeric codes.">
        <InputSummary inputs={result.inputs}/>
      </Panel>
      <div className="disclaimer-strip"><ShieldCheck size={17}/><span>Profile indicators are not feature attribution and do not explain model causality. A higher score does not prove a customer will default; a lower score does not guarantee repayment.</span></div>
      <div className="page-bottom-actions"><Link to="/prediction" className="button button-primary"><ArrowLeft size={15}/> Assess another profile</Link><Link to="/history" className="button button-secondary">View prediction history <ArrowRight size={15}/></Link></div>
    </>
  );
}

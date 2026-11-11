import { useCallback, useEffect, useState } from 'react';
import { Activity, Download, Info, Target, TrendingUp } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api, downloadCsv } from '../services/api';
import { ErrorState, LoadingState, MetricCard, PageHeading, Panel, formatPercent } from '../components/UI';

const definitions = [
  ['Accuracy', 'Share of all held-out test records classified correctly. It can hide missed defaults when the classes are imbalanced.'],
  ['Default precision', 'Among records flagged as default, how many were actual defaults in the held-out test set.'],
  ['Default recall', 'Among all actual defaults in the held-out test set, how many the model identified.'],
  ['F1-score', 'Harmonic mean of default precision and recall; balances the two measures.'],
  ['ROC-AUC', 'How well the model ranks default cases above non-default cases across possible thresholds.'],
  ['Average precision', 'Summarises the precision-recall curve and is useful when the positive class is less common.'],
  ['Brier score', 'Mean squared error of the model scores against the binary test outcome. Lower is better, but it is not a calibration certificate.'],
];

export default function Performance() {
  const [data, setData] = useState(null); const [error, setError] = useState('');
  const load = useCallback(() => { setError(''); api.performance().then(setData).catch((err) => setError(err.message)); }, []);
  useEffect(() => { load(); }, [load]);
  if (error) return <><PageHeading eyebrow="MODEL GOVERNANCE" title="Model performance" description="Evaluation results from the untouched held-out test set and the separate validation set."/><ErrorState message={error} onRetry={load}/></>;
  if (!data) return <LoadingState label="Loading model evaluation reports…"/>;

  const m = data.metrics || {}; const cm = data.confusion_matrix?.rows || [[0,0],[0,0]];
  const matrix = [
    { actual: 'Actual · No default', predictedNo: cm[0][0], predictedDefault: cm[0][1] },
    { actual: 'Actual · Default', predictedNo: cm[1][0], predictedDefault: cm[1][1] },
  ];
  const validation = (data.validation_comparison || []).map((item) => ({ ...item, accuracy_pct: item.accuracy * 100, precision_pct: item.precision_default * 100, recall_pct: item.recall_default * 100, f1_pct: item.f1_default * 100 }));
  const thresholdRows = (data.threshold_tradeoff || []).map((item) => ({ ...item, threshold_pct: item.threshold * 100, precision_pct: item.precision * 100, recall_pct: item.recall * 100, f1_pct: item.f1 * 100 }));
  const definitionsMap = data.metric_explanations || {};
  const explain = (key) => definitionsMap[key] || '';
  return (
    <>
      <PageHeading eyebrow="MODEL GOVERNANCE" title="Model performance" description="Evaluation results from the held-out test set, with validation comparisons and threshold trade-offs." action={<button className="button button-secondary" onClick={() => downloadCsv('creditrisk-held-out-test-metrics.csv', [m])}><Download size={16}/> Export metrics</button>}/>
      <div className="metric-grid metric-grid-four">
        <MetricCard label="Accuracy" value={formatPercent(m.accuracy)} detail="Overall correct classifications" icon={Target} tone="blue" footnote={explain('accuracy')}/>
        <MetricCard label="Default precision" value={formatPercent(m.precision_default)} detail="Reliability of default flags" icon={Target} tone="teal" footnote={explain('precision_default')}/>
        <MetricCard label="Default recall" value={formatPercent(m.recall_default)} detail="Actual defaults identified" icon={Activity} tone="amber" footnote={explain('recall_default')}/>
        <MetricCard label="ROC-AUC" value={m.roc_auc == null ? '—' : Number(m.roc_auc).toFixed(3)} detail="Ranking discrimination" icon={TrendingUp} tone="violet" footnote={explain('roc_auc')}/>
      </div>
      <div className="dashboard-grid dashboard-grid-two">
        <Panel title="Held-out test confusion matrix" subtitle="Actual outcomes versus predictions at the saved technical threshold of 0.50.">
          <div className="confusion-matrix"><div className="cm-axis-label">PREDICTED CLASS</div><div className="cm-header"><span>NO DEFAULT</span><span>DEFAULT</span></div>{matrix.map((row, index) => <div className="cm-row" key={row.actual}><div className="cm-row-label">{index === 0 ? 'ACTUAL · NO DEFAULT' : 'ACTUAL · DEFAULT'}</div><div className={`cm-cell ${index === 0 ? 'cm-correct' : 'cm-error'}`}><strong>{row.predictedNo.toLocaleString('en-IN')}</strong><span>{index === 0 ? 'True negative' : 'False negative'}</span></div><div className={`cm-cell ${index === 1 ? 'cm-correct-positive' : 'cm-error'}`}><strong>{row.predictedDefault.toLocaleString('en-IN')}</strong><span>{index === 0 ? 'False positive' : 'True positive'}</span></div></div>)}</div>
          <div className="matrix-summary"><span>TN <b>{m.tn?.toLocaleString('en-IN') ?? '—'}</b></span><span>FP <b>{m.fp?.toLocaleString('en-IN') ?? '—'}</b></span><span>FN <b>{m.fn?.toLocaleString('en-IN') ?? '—'}</b></span><span>TP <b>{m.tp?.toLocaleString('en-IN') ?? '—'}</b></span></div>
          <div className="insight-callout"><div className="callout-icon"><Info size={17}/></div><p>At this threshold, the model missed <strong>{m.fn?.toLocaleString('en-IN') ?? '—'}</strong> actual default cases in the held-out test set. False negatives matter when evaluating a monitoring system.</p></div>
        </Panel>
        <Panel title="Validation model comparison" subtitle="Candidate models compared on validation data; Random Forest was selected using default-class F1 with ROC-AUC as tie-break.">
          {validation.length ? <><ResponsiveContainer width="100%" height={265}><BarChart data={validation} margin={{ top: 8, right: 8, left: -20, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--chart-grid)"/><XAxis dataKey="model" tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} interval={0}/><YAxis domain={[0,100]} tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 10 }}/><Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'F1-score']}/><Bar dataKey="f1_pct" name="Default F1-score" radius={[5,5,0,0]}>{validation.map((item) => <Cell key={item.model} fill={item.model === m.model ? '#0F9F9A' : '#93A9B7'}/>)}</Bar></BarChart></ResponsiveContainer><div className="validation-mini-table">{validation.map((item) => <div className="validation-row" key={item.model}><span>{item.model}{item.model === m.model && <i className="selected-tag">Selected</i>}</span><b>{Number(item.f1_default).toFixed(3)}</b><small>F1</small></div>)}</div><button className="text-button" onClick={() => downloadCsv('creditrisk-validation-model-comparison.csv', validation)}><Download size={14}/> Export comparison</button></> : <div className="chart-empty">Validation model comparison file is not present.</div>}
        </Panel>
      </div>
      <Panel title="Threshold trade-off on validation data" subtitle="Illustrates how precision and recall change when the decision threshold changes. These are validation results, not held-out test retuning.">
        {thresholdRows.length ? <><ResponsiveContainer width="100%" height={280}><LineChart data={thresholdRows} margin={{ top: 10, right: 16, left: -20, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)"/><XAxis dataKey="threshold_pct" tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 11 }}/><YAxis domain={[0,100]} tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 11 }}/><Tooltip labelFormatter={(v) => `Threshold ${v}%`} formatter={(v, name) => [`${Number(v).toFixed(1)}%`, name]}/><Legend/><Line type="monotone" dataKey="precision_pct" name="Precision" stroke="#3686B5" strokeWidth={2.5} dot={{ r: 3 }}/><Line type="monotone" dataKey="recall_pct" name="Recall" stroke="#0F9F9A" strokeWidth={2.5} dot={{ r: 3 }}/><Line type="monotone" dataKey="f1_pct" name="F1-score" stroke="#C18B4A" strokeWidth={2.5} dot={{ r: 3 }}/></LineChart></ResponsiveContainer><div className="chart-meta-row"><span>{thresholdRows.length} recorded validation thresholds</span><button className="text-button" onClick={() => downloadCsv('creditrisk-validation-threshold-tradeoff.csv', data.threshold_tradeoff)}><Download size={14}/> Export trade-off data</button></div></> : <div className="chart-empty">Threshold trade-off report is not present.</div>}
      </Panel>
      <Panel title="Metric glossary" subtitle="What each evaluation measure tells a business audience.">
        <div className="glossary-grid">{definitions.map(([name, text]) => <div className="glossary-item" key={name}><strong>{name}</strong><p>{text}</p></div>)}</div>
      </Panel>
      <div className="assessment-notice"><Info size={18}/><div><strong>Interpretation and limitations</strong><span>The saved model scores are not separately calibrated. Demographic features are included, and no current Indian portfolio validation or formal fairness review has been completed. The 0.50 threshold is technical, not a bank-approved operating policy.</span></div></div>
    </>
  );
}

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Download, Filter, RefreshCw, Search, Trash2 } from 'lucide-react';
import { api, downloadCsv } from '../services/api';
import { ErrorState, LoadingState, PageHeading, Panel, EmptyState, formatDate, formatPercent } from '../components/UI';

export default function History() {
  const [data, setData] = useState(null); const [error, setError] = useState('');
  const [search, setSearch] = useState(''); const [filter, setFilter] = useState('all'); const [busy, setBusy] = useState(false);
  const load = useCallback(() => {
    setError('');
    return api.history(500).then((value) => { setData(value); return value; }).catch((err) => { setError(err.message); });
  }, []);
  useEffect(() => { load(); }, [load]);
  const items = data?.items || [];
  const visible = useMemo(() => items.filter((item) => {
    const matchesSearch = `assessment ${item.id} ${item.category}`.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || (filter === 'flagged' ? item.technical_prediction : !item.technical_prediction);
    return matchesSearch && matchesFilter;
  }), [items, search, filter]);

  async function clearAll() {
    if (!window.confirm('Delete all locally saved prediction history? This cannot be undone.')) return;
    setBusy(true); setError('');
    try { await api.clearHistory(); await load(); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  if (error && !data) return <><PageHeading eyebrow="AUDIT TRAIL" title="Prediction history" description="Review assessments generated through this application."/><ErrorState message={error} onRetry={load}/></>;
  if (!data) return <LoadingState label="Loading prediction history…"/>;
  return (
    <>
      <PageHeading eyebrow="AUDIT TRAIL" title="Prediction history" description="A local record of real prediction requests made through this API instance." action={<button className="button button-secondary" disabled={!items.length} onClick={() => downloadCsv('creditrisk-prediction-history.csv', items.map(({ id, created_at, score, category, technical_prediction, threshold }) => ({ id, created_at, score, category, technical_prediction, threshold })))}><Download size={16}/> Export history</button>}/>
      <div className="metric-grid metric-grid-three">
        <div className="compact-stat"><span>Total saved assessments</span><strong>{data.total}</strong></div>
        <div className="compact-stat"><span>Default flags at model cutoff</span><strong>{items.filter((item) => item.technical_prediction).length}</strong></div>
        <div className="compact-stat"><span>Displayed records</span><strong>{visible.length}</strong></div>
      </div>
      <Panel title="Assessment log" subtitle="Select a record to inspect its score, profile indicators, and submitted inputs." action={<button className="button button-ghost button-small" onClick={load}><RefreshCw size={14}/> Refresh</button>}>
        <div className="history-toolbar"><label className="search-box"><Search size={16}/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by assessment or category"/></label><label className="filter-select"><Filter size={15}/><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="all">All classifications</option><option value="flagged">Default flag</option><option value="clear">No default flag</option></select></label><button className="button button-danger-ghost button-small" onClick={clearAll} disabled={!items.length || busy}><Trash2 size={14}/>{busy ? 'Clearing…' : 'Clear history'}</button></div>
        {visible.length ? <div className="table-scroll"><table className="data-table"><thead><tr><th>Assessment</th><th>Date & time</th><th>Model score</th><th>Score category</th><th>Technical flag</th><th></th></tr></thead><tbody>{visible.map((item) => <tr key={item.id}><td><strong>#{item.id}</strong></td><td>{formatDate(item.created_at)}</td><td><strong>{formatPercent(item.score)}</strong></td><td><span className="table-category">{item.category}</span></td><td><span className={`flag-badge ${item.technical_prediction ? 'flagged' : 'not-flagged'}`}>{item.technical_prediction ? 'Default flag' : 'No default flag'}</span></td><td><Link className="table-open" to={`/results/${item.id}`}>View <span>→</span></Link></td></tr>)}</tbody></table></div> : <EmptyState title={items.length ? 'No matching assessments' : 'No history yet'} description={items.length ? 'Try a different search or filter.' : 'Predictions will be recorded here after successful API requests.'} action={!items.length && <Link to="/prediction" className="button button-primary button-small">Run first assessment</Link>}/>} 
      </Panel>
      <p className="chart-disclaimer">History is stored in a local SQLite database on the backend host. For a hosted production deployment, configure persistent storage and access controls before storing real customer data.</p>
    </>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight, CheckCircle2, RotateCcw, Sparkles, WandSparkles } from 'lucide-react';
import { api } from '../services/api';
import { PageHeading } from '../components/UI';

const DEFAULT_FORM = {
  LIMIT_BAL: 200000, SEX: 2, EDUCATION: 2, MARRIAGE: 2, AGE: 35,
  PAY_0: 0, PAY_2: 0, PAY_3: 0, PAY_4: 0, PAY_5: 0, PAY_6: 0,
  BILL_AMT1: 50000, BILL_AMT2: 48000, BILL_AMT3: 45000, BILL_AMT4: 42000, BILL_AMT5: 40000, BILL_AMT6: 38000,
  PAY_AMT1: 5000, PAY_AMT2: 5000, PAY_AMT3: 4500, PAY_AMT4: 4000, PAY_AMT5: 4000, PAY_AMT6: 4000,
};

const SEX = [{ value: 1, label: 'Male' }, { value: 2, label: 'Female' }];
const EDUCATION = [
  { value: 0, label: 'Not reported / unknown' }, { value: 1, label: 'Graduate school' },
  { value: 2, label: 'University' }, { value: 3, label: 'High school' }, { value: 4, label: 'Other' },
  { value: 5, label: 'Unknown (source code 5)' }, { value: 6, label: 'Unknown (source code 6)' },
];
const MARRIAGE = [{ value: 0, label: 'Not reported / unknown' }, { value: 1, label: 'Married' }, { value: 2, label: 'Single / unmarried' }, { value: 3, label: 'Other' }];
const PAY = [
  { value: -2, label: 'No consumption recorded' }, { value: -1, label: 'Paid duly / on time' },
  { value: 0, label: 'Revolving credit (no recorded delay)' }, ...Array.from({ length: 8 }, (_, i) => ({ value: i + 1, label: `Payment delayed by ${i + 1} month${i ? 's' : ''}` })),
];
const MONTHS = ['September 2005', 'August 2005', 'July 2005', 'June 2005', 'May 2005', 'April 2005'];
const DEMOS = {
  'On-time payment example': { ...DEFAULT_FORM, LIMIT_BAL: 500000, SEX: 2, EDUCATION: 1, MARRIAGE: 2, AGE: 38, PAY_0: -1, PAY_2: -1, PAY_3: -1, PAY_4: -1, PAY_5: -1, PAY_6: -1, BILL_AMT1: 24000, BILL_AMT2: 22000, BILL_AMT3: 21000, BILL_AMT4: 20000, BILL_AMT5: 19000, BILL_AMT6: 18000, PAY_AMT1: 25000, PAY_AMT2: 23000, PAY_AMT3: 22000, PAY_AMT4: 20000, PAY_AMT5: 19000, PAY_AMT6: 18000 },
  'Recent delay example': { ...DEFAULT_FORM, LIMIT_BAL: 50000, SEX: 1, EDUCATION: 3, MARRIAGE: 1, AGE: 29, PAY_0: 2, PAY_2: 2, PAY_3: 1, PAY_4: 1, PAY_5: 0, PAY_6: 0, BILL_AMT1: 48000, BILL_AMT2: 46000, BILL_AMT3: 44000, BILL_AMT4: 42000, BILL_AMT5: 40000, BILL_AMT6: 38000, PAY_AMT1: 1000, PAY_AMT2: 1000, PAY_AMT3: 1000, PAY_AMT4: 1500, PAY_AMT5: 2000, PAY_AMT6: 2000 },
  'Mixed history example': { ...DEFAULT_FORM, LIMIT_BAL: 150000, SEX: 2, EDUCATION: 2, MARRIAGE: 2, AGE: 42, PAY_0: 1, PAY_2: 0, PAY_3: -1, PAY_4: 0, PAY_5: -1, PAY_6: 0, BILL_AMT1: 82000, BILL_AMT2: 77000, BILL_AMT3: 74000, BILL_AMT4: 68000, BILL_AMT5: 63000, BILL_AMT6: 59000, PAY_AMT1: 6000, PAY_AMT2: 5000, PAY_AMT3: 7000, PAY_AMT4: 5000, PAY_AMT5: 4000, PAY_AMT6: 4000 },
};

function Field({ label, help, children }) {
  return <label className="field"><span>{label}</span>{children}{help && <small>{help}</small>}</label>;
}
function NumberInput({ field, label, value, onChange, min = 0, max = 5000000, step = 1000, help }) {
  return <Field label={label} help={help}><input type="number" inputMode="decimal" min={min} max={max} step={step} value={value} onChange={(event) => onChange(field, Number(event.target.value))} required /></Field>;
}
function SelectInput({ field, label, value, options, onChange }) {
  return <Field label={label}><select value={value} onChange={(event) => onChange(field, Number(event.target.value))}>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></Field>;
}

export default function Prediction() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [lookups, setLookups] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  useEffect(() => { api.config().then(setLookups).catch(() => {}); }, []);
  const categories = lookups?.categories || { gender: SEX, education: EDUCATION, marital_status: MARRIAGE, repayment_status: PAY };
  const months = lookups?.months ? Array.from({ length: 6 }, (_, index) => lookups.months[String(index + 1)] || MONTHS[index]) : MONTHS;
  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError('');
    try {
      const result = await api.predict(form);
      navigate(`/results/${result.id}`, { state: { result } });
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  const formatCurrency = (value) => `NT$ ${Number(value).toLocaleString('en-IN')}`;
  return (
    <>
      <PageHeading eyebrow="MODEL WORKSPACE" title="Customer risk assessment" description="Build a historical customer profile and submit it to the saved Random Forest pipeline. Your original model inputs and preprocessing remain unchanged." />
      <div className="assessment-notice"><AlertCircle size={18}/><div><strong>Academic decision-support prototype</strong><span>The model score is not calibrated and is not a verified probability of default. Never use it for automated credit approval, rejection, collections, pricing, or adverse customer action.</span></div></div>
      <div className="demo-toolbar"><div><div className="demo-title"><WandSparkles size={17}/> Quick-fill examples</div><p>Populate the form with synthetic sample inputs, then run the real saved model.</p></div><div className="demo-actions">{Object.keys(DEMOS).map((name) => <button key={name} className="button button-secondary button-small" type="button" onClick={() => { setForm(DEMOS[name]); setError(''); }}>{name}</button>)}<button className="button button-ghost button-small" type="button" onClick={() => { setForm(DEFAULT_FORM); setError(''); }}><RotateCcw size={14}/> Reset</button></div></div>
      <form onSubmit={submit} className="assessment-form">
        <section className="form-card card">
          <div className="form-card-heading"><span className="step-number">01</span><div><h2>Customer & credit profile</h2><p>Basic attributes and approved credit limit as represented in the historical dataset.</p></div><span className="field-count">5 fields</span></div>
          <div className="form-grid form-grid-three">
            <NumberInput field="LIMIT_BAL" label="Credit limit (NT$)" value={form.LIMIT_BAL} min={0} max={2000000} step={10000} onChange={update} help="New Taiwan dollars (NT$)." />
            <SelectInput field="SEX" label="Gender" value={form.SEX} options={categories.gender} onChange={update}/>
            <NumberInput field="AGE" label="Age (years)" value={form.AGE} min={18} max={100} step={1} onChange={update}/>
            <SelectInput field="EDUCATION" label="Education level" value={form.EDUCATION} options={categories.education} onChange={update}/>
            <SelectInput field="MARRIAGE" label="Marital status" value={form.MARRIAGE} options={categories.marital_status} onChange={update}/>
          </div>
        </section>

        <section className="form-card card">
          <div className="form-card-heading"><span className="step-number">02</span><div><h2>Repayment history</h2><p>Select the recorded repayment status for each month. Dataset labels are shown instead of raw numeric codes.</p></div><span className="field-count">6 fields</span></div>
          <div className="form-grid form-grid-three">{['PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6'].map((field, index) => <SelectInput key={field} field={field} label={months[index]} value={form[field]} options={categories.repayment_status} onChange={update}/>)}</div>
        </section>

        <section className="form-card card">
          <div className="form-card-heading"><span className="step-number">03</span><div><h2>Historical bill statements</h2><p>Outstanding statement amounts from the six historical months.</p></div><span className="field-count">6 fields</span></div>
          <div className="form-grid form-grid-three">{Array.from({ length: 6 }, (_, i) => { const field = `BILL_AMT${i + 1}`; return <NumberInput key={field} field={field} label={`${months[i]} · bill amount`} value={form[field]} min={-1000000} max={5000000} step={1000} onChange={update} help={formatCurrency(form[field])}/>; })}</div>
        </section>

        <section className="form-card card">
          <div className="form-card-heading"><span className="step-number">04</span><div><h2>Previous payment amounts</h2><p>Payments recorded for each historical month.</p></div><span className="field-count">6 fields</span></div>
          <div className="form-grid form-grid-three">{Array.from({ length: 6 }, (_, i) => { const field = `PAY_AMT${i + 1}`; return <NumberInput key={field} field={field} label={`${months[i]} · payment amount`} value={form[field]} min={0} max={5000000} step={500} onChange={update} help={formatCurrency(form[field])}/>; })}</div>
        </section>
        {error && <div className="inline-error"><AlertCircle size={17}/><span>{error}</span></div>}
        <div className="form-submit-bar"><div><CheckCircle2 size={17}/><span>Inputs are validated by the Python API before prediction.</span></div><button type="submit" className="button button-primary button-large" disabled={busy}>{busy ? <><span className="button-spinner"/> Running saved model…</> : <>Generate assessment <ArrowRight size={16}/></>}</button></div>
      </form>
      <p className="form-footnote"><Sparkles size={14}/> Sample profiles are synthetic demonstration inputs. The prediction score is generated by your existing saved model; no sample output is hardcoded.</p>
    </>
  );
}

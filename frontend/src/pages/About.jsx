import { ArrowRight, BookOpen, BrainCircuit, Database, GitBranch, ShieldCheck, Workflow } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeading, Panel } from '../components/UI';

const steps = [
  ['01', 'Dataset audit', '30,000 historical customer records are checked for missing values, duplicates, identifiers, and target distribution.'],
  ['02', 'Exploratory analysis', 'Repayment status, credit-limit, age, and education group summaries are examined as descriptive associations.'],
  ['03', 'Preprocessing pipeline', 'Numeric and categorical predictors are transformed inside a scikit-learn pipeline to preserve the training workflow.'],
  ['04', 'Model selection', 'Logistic Regression, Decision Tree, and Random Forest are compared on a validation split.'],
  ['05', 'Held-out evaluation', 'The selected Random Forest is evaluated once on a separate test set with classification and ranking metrics.'],
  ['06', 'Decision-support interface', 'React sends the original 23 customer features to FastAPI, which loads the saved pipeline and returns its real output.'],
];

export default function About() {
  return (
    <>
      <PageHeading eyebrow="PROJECT INFORMATION" title="About CreditRisk Analytics" description="An MBA Business Analytics project exploring next-month credit-card default risk using machine learning and responsible decision-support design." action={<Link to="/performance" className="button button-secondary">View model evaluation <ArrowRight size={15}/></Link>}/>
      <div className="about-intro card"><div className="about-icon"><BrainCircuit size={30}/></div><div><div className="eyebrow">PROJECT PURPOSE</div><h2>Turn historical credit data into understandable signals.</h2><p>The platform demonstrates how portfolio analysis and a saved machine-learning pipeline can help organise information for qualified human review. It does not automate lending or collections decisions.</p></div></div>
      <div className="metric-grid metric-grid-three about-tech-grid">
        <div className="tech-card card"><Database size={21}/><strong>Data foundation</strong><span>UCI Default of Credit Card Clients · Taiwan · 2005</span></div>
        <div className="tech-card card"><BrainCircuit size={21}/><strong>Machine learning</strong><span>Scikit-learn Random Forest pipeline</span></div>
        <div className="tech-card card"><GitBranch size={21}/><strong>Application stack</strong><span>React · FastAPI · SQLite · Recharts</span></div>
      </div>
      <Panel title="Project workflow" subtitle="The interface uses the artifacts and model already present in the project repository.">
        <div className="workflow-list">{steps.map(([num, title, text], index) => <div className="workflow-step" key={num}><div className="workflow-number">{num}</div><div><strong>{title}</strong><p>{text}</p></div>{index < steps.length - 1 && <span className="workflow-connector"/>}</div>)}</div>
      </Panel>
      <div className="dashboard-grid dashboard-grid-two">
        <Panel title="What the model predicts" subtitle="Target definition"><div className="body-copy"><p>The target is <code>default payment next month</code>. The output score corresponds to class 1 in the saved classifier.</p><p>Inputs include credit limit, customer profile, repayment status for six historical months, bill statement amounts, and previous payment amounts.</p><p>Demographic fields remain part of the existing trained pipeline. They are not silently removed or remapped by this React upgrade.</p></div></Panel>
        <Panel title="What this project does not claim" subtitle="Responsible-use boundaries"><div className="body-copy"><p>The model score has not been separately calibrated. The technical 0.50 threshold is not a bank-approved business cutoff.</p><p>The dataset reflects Taiwan in 2005, not current Indian customers. There is no current portfolio validation, production fairness assessment, or approval for operational decisions.</p><p>Group-level charts show historical associations, not causal effects. Profile indicators are descriptive summaries, not explanations of model causality.</p></div></Panel>
      </div>
      <div className="assessment-notice"><ShieldCheck size={18}/><div><strong>Human oversight is mandatory</strong><span>This application is an academic prototype. It must not be used for automated credit approval, rejection, pricing, collections, or other adverse decisions. Any real use would require current external validation, probability calibration, fairness and legal review, security controls, and documented business governance.</span></div></div>
      <p className="source-note"><BookOpen size={15}/> Dataset source: <a href="https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients" target="_blank" rel="noreferrer">UCI Machine Learning Repository — Default of Credit Card Clients</a>.</p>
    </>
  );
}

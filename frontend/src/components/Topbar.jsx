import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Moon, Plus, Sun, Wifi, WifiOff } from 'lucide-react';
import { api } from '../services/api';

const titles = {
  '/': 'Overview', '/prediction': 'Risk assessment', '/results': 'Assessment results',
  '/insights': 'Data insights', '/performance': 'Model performance', '/history': 'Prediction history', '/about': 'About the project',
};

export default function Topbar({ onMenu, dark, onThemeToggle }) {
  const location = useLocation();
  const [health, setHealth] = useState(null);
  const title = location.pathname.startsWith('/results/') ? 'Assessment results' : (titles[location.pathname] || 'CreditRisk');

  useEffect(() => {
    let alive = true;
    const ping = () => api.health().then((value) => alive && setHealth(value)).catch(() => alive && setHealth({ status: 'offline' }));
    ping();
    const interval = window.setInterval(ping, 30000);
    return () => { alive = false; window.clearInterval(interval); };
  }, []);

  const online = health?.status === 'ok';
  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-button mobile-menu" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button>
        <div className="topbar-context"><span>Workspace</span><b>/</b><strong>{title}</strong></div>
      </div>
      <div className="topbar-right">
        <span className={`api-status ${online ? 'api-online' : 'api-offline'}`} title={health?.model_available ? 'API and model artifact available' : 'API or model is unavailable'}>
          {online ? <Wifi size={14} /> : <WifiOff size={14} />}{online ? 'API connected' : health?.status === 'degraded' ? 'Model unavailable' : 'API offline'}
        </span>
        <button className="icon-button" onClick={onThemeToggle} title={dark ? 'Switch to light mode' : 'Switch to dark mode'} aria-label="Toggle theme">{dark ? <Sun size={18} /> : <Moon size={18} />}</button>
        <Link to="/prediction" className="button button-primary topbar-action"><Plus size={16} /> New assessment</Link>
      </div>
    </header>
  );
}

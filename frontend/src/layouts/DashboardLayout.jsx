import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'motion/react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

export default function DashboardLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(() => localStorage.getItem('creditrisk-theme') === 'dark');
  const location = useLocation();

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    localStorage.setItem('creditrisk-theme', dark ? 'dark' : 'light');
  }, [dark]);

  useEffect(() => setMenuOpen(false), [location.pathname]);

  return (
    <div className={`app-shell ${collapsed ? 'app-shell-collapsed' : ''}`}>
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} collapsed={collapsed} onCollapse={() => setCollapsed((value) => !value)} />
      <div className="main-shell">
        <Topbar onMenu={() => setMenuOpen(true)} dark={dark} onThemeToggle={() => setDark((value) => !value)} />
        <main className="main-content">
          <AnimatePresence mode="wait">
            <motion.div key={location.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: 0.18 }}>
              <Outlet />
            </motion.div>
          </AnimatePresence>
          <footer className="app-footer"><span>CreditRisk Analytics</span><span>Academic prototype · Human review only</span></footer>
        </main>
      </div>
    </div>
  );
}

import { Navigate, Route, Routes } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Overview from './pages/Overview';
import Prediction from './pages/Prediction';
import Results from './pages/Results';
import Insights from './pages/Insights';
import Performance from './pages/Performance';
import History from './pages/History';
import About from './pages/About';

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route index element={<Overview />} />
        <Route path="prediction" element={<Prediction />} />
        <Route path="results" element={<Results />} />
        <Route path="results/:id" element={<Results />} />
        <Route path="insights" element={<Insights />} />
        <Route path="performance" element={<Performance />} />
        <Route path="history" element={<History />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

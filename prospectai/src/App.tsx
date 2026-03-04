import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Leads } from './pages/Leads';
import { Pipelines } from './pages/Pipelines';
import { Sequences } from './pages/Sequences';
import { Messages } from './pages/Messages';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { Scraping } from './pages/Scraping';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="leads" element={<Leads />} />
          <Route path="pipelines" element={<Pipelines />} />
          <Route path="sequences" element={<Sequences />} />
          <Route path="scraping" element={<Scraping />} />
          <Route path="messages" element={<Messages />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  );
}

import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';

const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Leads = lazy(() => import('./pages/Leads').then(m => ({ default: m.Leads })));
const Pipelines = lazy(() => import('./pages/Pipelines').then(m => ({ default: m.Pipelines })));
const Sequences = lazy(() => import('./pages/Sequences').then(m => ({ default: m.Sequences })));
const Messages = lazy(() => import('./pages/Messages').then(m => ({ default: m.Messages })));
const Analytics = lazy(() => import('./pages/Analytics').then(m => ({ default: m.Analytics })));
const Settings = lazy(() => import('./pages/Settings').then(m => ({ default: m.Settings })));
const Scraping = lazy(() => import('./pages/Scraping').then(m => ({ default: m.Scraping })));
const Changelog = lazy(() => import('./pages/Changelog').then(m => ({ default: m.Changelog })));
const Templates = lazy(() => import('./pages/Templates').then(m => ({ default: m.Templates })));

const LoadingFallback = () => (
  <div className="flex h-[80vh] w-full flex-col items-center justify-center space-y-4">
    <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent shadow-md"></div>
    <p className="text-sm text-text-secondary animate-pulse">Chargement de l'interface...</p>
  </div>
);

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={
            <Suspense fallback={<LoadingFallback />}><Dashboard /></Suspense>
          } />
          <Route path="leads" element={
            <Suspense fallback={<LoadingFallback />}><Leads /></Suspense>
          } />
          <Route path="pipelines" element={
            <Suspense fallback={<LoadingFallback />}><Pipelines /></Suspense>
          } />
          <Route path="sequences" element={
            <Suspense fallback={<LoadingFallback />}><Sequences /></Suspense>
          } />
          <Route path="scraping" element={
            <Suspense fallback={<LoadingFallback />}><Scraping /></Suspense>
          } />
          <Route path="templates" element={
            <Suspense fallback={<LoadingFallback />}><Templates /></Suspense>
          } />
          <Route path="changelog" element={
            <Suspense fallback={<LoadingFallback />}><Changelog /></Suspense>
          } />
          <Route path="messages" element={
            <Suspense fallback={<LoadingFallback />}><Messages /></Suspense>
          } />
          <Route path="analytics" element={
            <Suspense fallback={<LoadingFallback />}><Analytics /></Suspense>
          } />
          <Route path="settings" element={
            <Suspense fallback={<LoadingFallback />}><Settings /></Suspense>
          } />
          <Route path="*" element={
            <div className="flex h-[80vh] w-full flex-col items-center justify-center space-y-4">
              <h1 className="text-4xl font-bold text-text-primary">404</h1>
              <p className="text-text-secondary">Page introuvable</p>
              <a href="/" className="px-4 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity">Retour au tableau de bord</a>
            </div>
          } />
        </Route>
      </Routes>
    </Router>
  );
}

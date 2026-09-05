import React, { useEffect, useState } from 'react';
import { Header } from './components/common/Header';
import { Navigation, ActiveTab } from './components/common/Navigation';
import { LandingPage } from './pages/LandingPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { ObservationsPage } from './pages/ObservationsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ModelPage } from './pages/ModelPage';
import { JobsPage } from './pages/JobsPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { api } from './services/api';
import { DetectionSummaryStats, SystemHealthResponse } from './types';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [stats, setStats] = useState<DetectionSummaryStats | null>(null);
  const [health, setHealth] = useState<SystemHealthResponse | null>(null);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [healthData, statsData] = await Promise.all([
          api.getHealth(),
          api.getDetectionStats(),
        ]);
        setHealth(healthData);
        setStats(statsData);
      } catch (error) {
        console.error('Failed to load dashboard summaries:', error);
      }
    };

    loadDashboard();
  }, []);

  const renderMainPanel = () => {
    switch (activeTab) {
      case 'workspace':
        return <WorkspacePage />;
      case 'observations':
        return <ObservationsPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'model':
        return <ModelPage />;
      case 'jobs':
        return <JobsPage />;
      case 'methodology':
        return <MethodologyPage />;
      case 'overview':
      default:
        return (
          <LandingPage
            stats={stats}
            health={health}
            onEnterWorkspace={() => setActiveTab('workspace')}
            onNavigateTab={(tab) => setActiveTab(tab as ActiveTab)}
          />
        );
    }
  };

  return (
    <div className="app-container">
      <Header health={health} onNavigateLanding={() => setActiveTab('overview')} />
      <Navigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        detectionCount={stats?.total_detections ?? 0}
        observationCount={4}
      />
      <main className="main-content-viewport">{renderMainPanel()}</main>
    </div>
  );
};

export default App;

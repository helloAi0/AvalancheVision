import React from 'react';
import { 
  Compass, 
  Map, 
  BarChart3, 
  Satellite, 
  Layers, 
  Cpu, 
  BookOpen 
} from 'lucide-react';

export type ActiveTab = 'overview' | 'workspace' | 'observations' | 'analytics' | 'model' | 'jobs' | 'methodology';

interface NavigationProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  detectionCount: number;
  observationCount: number;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  onTabChange,
  detectionCount,
  observationCount,
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { 
      id: 'workspace', 
      label: 'GIS Workstation', 
      icon: Map, 
      count: detectionCount > 0 ? detectionCount : undefined 
    },
    { 
      id: 'observations', 
      label: 'SAR Observations', 
      icon: Satellite, 
      count: observationCount > 0 ? observationCount : undefined 
    },
    { id: 'analytics', label: 'Scientific Analytics', icon: BarChart3 },
    { id: 'model', label: 'Model Explorer', icon: Layers },
    { id: 'jobs', label: 'Job Console', icon: Cpu },
    { id: 'methodology', label: 'Methodology & Provenance', icon: BookOpen },
  ];

  return (
    <nav className="nav-tab-bar" aria-label="Main Navigation">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            id={`nav-btn-${tab.id}`}
            className={`nav-tab-btn ${isActive ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id as ActiveTab)}
          >
            <Icon size={15} />
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className="nav-badge-count">{tab.count}</span>
            )}
          </button>
        );
      })}
    </nav>
  );
};

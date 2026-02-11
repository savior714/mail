
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Rules from './pages/Rules';
import Pipeline from './pages/Pipeline';
import Settings from './pages/Settings';

const App: React.FC = () => {
  return (
    <Router>
      <div className="flex h-screen w-screen overflow-hidden bg-[#fdfbf7]">
        {/* Sidebar: Fixed width, full height */}
        <Sidebar />

        {/* Main Content: Flex grow, scrollable */}
        <div className="flex-1 h-full overflow-y-auto p-8 relative">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;

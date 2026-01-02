import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen text-slate-200">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            {/* Future routes can go here */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import InboxView from './components/InboxView';
import PlanReviewView from './components/PlanReviewView';
import DepartureChecklistView from './components/DepartureChecklistView';
import ActiveTripView from './components/ActiveTripView';
import {
  fetchAIStatus,
  fetchErrands,
  planProposedTrip,
  startNewTrip,
  fetchActiveTrip,
} from './api';
import './App.css';

export default function App() {
  const [currentView, setCurrentView] = useState('inbox');
  const [errands, setErrands] = useState([]);
  const [aiStatus, setAiStatus] = useState(null);
  const [proposedPlan, setProposedPlan] = useState(null);
  const [activeTrip, setActiveTrip] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load initial data
  const loadInitialData = async () => {
    try {
      const [ai, errs, tripResp] = await Promise.all([
        fetchAIStatus().catch(() => ({ available: false, active_engine: 'Built-in Fast NLP' })),
        fetchErrands().catch(() => []),
        fetchActiveTrip().catch(() => ({ active: false, trip: null })),
      ]);

      setAiStatus(ai);
      setErrands(errs);

      if (tripResp.active && tripResp.trip) {
        setActiveTrip(tripResp.trip);
        setCurrentView('trip');
      }
    } catch (err) {
      console.error('Initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const refreshErrands = async () => {
    try {
      const errs = await fetchErrands();
      setErrands(errs);
    } catch (err) {
      console.error('Failed to refresh errands:', err);
    }
  };

  const refreshActiveTrip = async () => {
    try {
      const tripResp = await fetchActiveTrip();
      if (tripResp.active && tripResp.trip) {
        setActiveTrip(tripResp.trip);
      } else {
        setActiveTrip(null);
      }
    } catch (err) {
      console.error('Failed to refresh active trip:', err);
    }
  };

  const handleProceedToPlan = async () => {
    try {
      const plan = await planProposedTrip();
      setProposedPlan(plan);
      setCurrentView('plan');
    } catch (err) {
      alert('Could not generate plan: ' + err.message);
    }
  };

  const handleStartTrip = async (name, plan) => {
    const newTrip = await startNewTrip(name, plan);
    setActiveTrip(newTrip);
    setCurrentView('trip');
    await refreshErrands();
  };

  const handleTripCompleted = async () => {
    setActiveTrip(null);
    setProposedPlan(null);
    await refreshErrands();
    setCurrentView('inbox');
  };

  if (loading) {
    return (
      <div className="app-loading-screen">
        <div className="spinner"></div>
        <p>Loading ErrandQuest...</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header
        currentView={currentView}
        setView={setCurrentView}
        aiStatus={aiStatus}
        activeTrip={activeTrip}
      />

      <main className="app-main">
        {currentView === 'inbox' && (
          <InboxView
            errands={errands}
            onRefreshErrands={refreshErrands}
            onProceedToPlan={handleProceedToPlan}
          />
        )}

        {currentView === 'plan' && (
          <PlanReviewView
            proposedPlan={proposedPlan}
            setProposedPlan={setProposedPlan}
            onBackToInbox={() => setCurrentView('inbox')}
            onProceedToDeparture={() => setCurrentView('departure')}
          />
        )}

        {currentView === 'departure' && (
          <DepartureChecklistView
            proposedPlan={proposedPlan}
            onBackToPlan={() => setCurrentView('plan')}
            onStartTrip={handleStartTrip}
          />
        )}

        {currentView === 'trip' && (
          <ActiveTripView
            activeTrip={activeTrip}
            onRefreshTrip={refreshActiveTrip}
            onTripCompleted={handleTripCompleted}
            onGoToInbox={() => setCurrentView('inbox')}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>ErrandQuest — Touch Grass & Get Things Done in One Trip 🌱</p>
      </footer>
    </div>
  );
}

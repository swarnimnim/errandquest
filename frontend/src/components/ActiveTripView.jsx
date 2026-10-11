import React, { useState } from 'react';
import { updateTripItem, updatePackingItem, completeTrip } from '../api';

export default function ActiveTripView({
  activeTrip,
  onRefreshTrip,
  onTripCompleted,
  onGoToInbox,
}) {
  const [summaryData, setSummaryData] = useState(null);
  const [isFinishing, setIsFinishing] = useState(false);
  const [showPackingDrawer, setShowPackingDrawer] = useState(false);

  if (!activeTrip) {
    return (
      <div className="view-container">
        <div className="section-card empty-state">
          <div className="empty-icon">🚶‍♂️</div>
          <h3>No Active Outing In Progress</h3>
          <p>Plan your trip and start it from the Departure checklist to view your live execution checklist here.</p>
          <button className="btn btn-primary" onClick={onGoToInbox}>
            ← Go to Errand Inbox
          </button>
        </div>
      </div>
    );
  }

  const { stops = [], items = [], packing_items = [] } = activeTrip;

  const totalTasks = items.length;
  const completedTasks = items.filter((it) => it.completed).length;
  const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const handleToggleTask = async (item) => {
    try {
      await updateTripItem(activeTrip.id, item.item_id, !item.completed);
      onRefreshTrip();
    } catch (err) {
      alert('Failed to update task: ' + err.message);
    }
  };

  const handleTogglePacking = async (pack) => {
    try {
      await updatePackingItem(activeTrip.id, pack.id, !pack.checked);
      onRefreshTrip();
    } catch (err) {
      alert('Failed to update packing item: ' + err.message);
    }
  };

  const handleFinishTrip = async () => {
    const uncompletedCount = totalTasks - completedTasks;
    const confirmMsg =
      uncompletedCount > 0
        ? `You have ${uncompletedCount} unfinished task(s). They will be safely carried forward into your next outing. End trip now?`
        : 'All tasks completed! End this outing?';

    if (!window.confirm(confirmMsg)) return;

    setIsFinishing(true);
    try {
      const summary = await completeTrip(activeTrip.id);
      setSummaryData(summary);
    } catch (err) {
      alert('Failed to end trip: ' + err.message);
    } finally {
      setIsFinishing(false);
    }
  };

  return (
    <div className="view-container active-trip-view">
      {/* Active Trip Header */}
      <div className="outing-header-card">
        <div className="outing-top-row">
          <div>
            <span className="live-pill">● LIVE OUTING</span>
            <h2 className="outing-title">{activeTrip.name}</h2>
          </div>
          <button
            className="btn btn-danger small"
            onClick={handleFinishTrip}
            disabled={isFinishing}
          >
            {isFinishing ? 'Finishing...' : 'End Outing'}
          </button>
        </div>

        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-label-row">
            <span>Progress: {completedTasks} of {totalTasks} errands completed</span>
            <span className="progress-pct">{progressPercent}%</span>
          </div>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        {/* Packing Quick Check Toggle */}
        <button
          className="btn-link packing-toggle-btn"
          onClick={() => setShowPackingDrawer(!showPackingDrawer)}
        >
          🎒 {showPackingDrawer ? 'Hide Packed Essentials' : `View Packed Essentials (${packing_items.length})`}
        </button>

        {showPackingDrawer && (
          <div className="mini-packing-drawer">
            <h4>Bag Essentials:</h4>
            <div className="mini-packing-list">
              {packing_items.map((pack) => (
                <label key={pack.id} className="mini-pack-item">
                  <input
                    type="checkbox"
                    checked={!!pack.checked}
                    onChange={() => handleTogglePacking(pack)}
                  />
                  <span className={pack.checked ? 'packed-strikethrough' : ''}>
                    {pack.label}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Stop by Stop Execution */}
      <div className="outing-stops">
        {stops.map((stop, sIdx) => {
          const stopTasks = items.filter((it) => it.stop_id === stop.id);
          const stopCompleted =
            stopTasks.length > 0 && stopTasks.every((it) => it.completed);

          return (
            <div
              key={stop.id || sIdx}
              className={`trip-stop-card ${stopCompleted ? 'stop-done' : ''}`}
            >
              <div className="trip-stop-header">
                <span className="stop-badge">Stop #{stop.sequence_number}</span>
                <div className="stop-title-wrap">
                  <h3 className="trip-stop-name">{stop.name}</h3>
                  <span className="trip-stop-cat">{stop.category}</span>
                </div>
                {stopCompleted && (
                  <span className="stop-completed-badge">✓ Stop Done</span>
                )}
              </div>

              <div className="trip-tasks-list">
                {stopTasks.map((item) => (
                  <div
                    key={item.item_id}
                    className={`trip-task-row ${item.completed ? 'task-completed' : ''}`}
                    onClick={() => handleToggleTask(item)}
                  >
                    <input
                      type="checkbox"
                      className="large-checkbox"
                      checked={!!item.completed}
                      onChange={() => {}} // handled by row click
                    />
                    <div className="trip-task-content">
                      <span className="trip-task-title">{item.title}</span>
                      <div className="trip-task-meta">
                        {item.deadline && (
                          <span className="badge badge-deadline">⏰ {item.deadline}</span>
                        )}
                        {item.urgency === 'high' && (
                          <span className="badge badge-urgent">🔥 Urgent</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Sticky Action */}
      <div className="active-trip-footer">
        <button
          className="btn btn-primary full-width large-tap"
          onClick={handleFinishTrip}
          disabled={isFinishing}
        >
          {completedTasks === totalTasks
            ? '🎉 All Done! Finish Outing'
            : '🏁 End Outing & Save Unfinished'}
        </button>
      </div>

      {/* Trip Completion Summary Modal (FR-09) */}
      {summaryData && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <span className="modal-icon">🌱</span>
              <h2>Trip Complete!</h2>
              <p>You touched grass and got things done in one organized outing.</p>
            </div>

            <div className="summary-stats-grid">
              <div className="summary-stat-box">
                <span className="stat-num completed-stat">
                  {summaryData.completed_tasks}
                </span>
                <span className="stat-label">Tasks Completed</span>
              </div>
              <div className="summary-stat-box">
                <span className="stat-num stops-stat">
                  {summaryData.stops_visited}
                </span>
                <span className="stat-label">Stops Visited</span>
              </div>
              <div className="summary-stat-box">
                <span className="stat-num carry-stat">
                  {summaryData.carried_forward}
                </span>
                <span className="stat-label">Carried Forward</span>
              </div>
            </div>

            {summaryData.carried_forward > 0 ? (
              <p className="summary-note">
                ✨ {summaryData.carried_forward} unfinished task(s) have been saved
                to your inbox for your next trip!
              </p>
            ) : (
              <p className="summary-note">
                🎉 Everything was finished in this single trip! No return trip needed.
              </p>
            )}

            <button
              className="btn btn-primary full-width"
              onClick={() => {
                setSummaryData(null);
                onTripCompleted();
              }}
            >
              Return to Inbox
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

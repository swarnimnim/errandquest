import React from 'react';

export default function PlanReviewView({
  proposedPlan,
  setProposedPlan,
  onBackToInbox,
  onProceedToDeparture,
}) {
  if (!proposedPlan || !proposedPlan.ordered_stops || proposedPlan.ordered_stops.length === 0) {
    return (
      <div className="view-container">
        <div className="section-card empty-state">
          <div className="empty-icon">🗺️</div>
          <h3>No Trip Plan Generated Yet</h3>
          <p>Go back to the inbox and click "Plan Trip Now" to generate an organized itinerary.</p>
          <button className="btn btn-primary" onClick={onBackToInbox}>
            ← Go to Inbox
          </button>
        </div>
      </div>
    );
  }

  const handleMoveStop = (index, direction) => {
    const newStops = [...proposedPlan.ordered_stops];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newStops.length) return;

    const temp = newStops[index];
    newStops[index] = newStops[targetIndex];
    newStops[targetIndex] = temp;

    // Re-assign sequence numbers
    newStops.forEach((s, idx) => {
      s.sequence_number = idx + 1;
    });

    setProposedPlan({
      ...proposedPlan,
      ordered_stops: newStops,
    });
  };

  return (
    <div className="view-container plan-view">
      <div className="section-card">
        <div className="plan-header-row">
          <div>
            <h2 className="section-title">
              <span>🗺️</span> Review Your Trip Plan
            </h2>
            <p className="section-subtitle">
              We grouped your errands into stops and ordered them practically (e.g. cash first, groceries last).
              You can reorder stops as you prefer.
            </p>
          </div>

          <div className="plan-stats-badges">
            <span className="stat-badge">
              <strong>{proposedPlan.total_stops}</strong> Stops
            </span>
            <span className="stat-badge">
              <strong>{proposedPlan.total_tasks}</strong> Errands
            </span>
          </div>
        </div>

        <div className="stops-list">
          {proposedPlan.ordered_stops.map((stop, index) => {
            const hasPerishable = stop.tasks.some((t) => t.is_perishable);
            const isBanking = stop.name.includes('Bank') || stop.name.includes('ATM');

            return (
              <div key={index} className="stop-card">
                <div className="stop-card-header">
                  <div className="stop-order-pill">Stop #{stop.sequence_number}</div>
                  <div className="stop-info">
                    <h3 className="stop-name">{stop.name}</h3>
                    <span className="stop-category">{stop.category}</span>
                  </div>

                  <div className="stop-reorder-btns">
                    <button
                      className="btn-icon small"
                      disabled={index === 0}
                      onClick={() => handleMoveStop(index, -1)}
                      title="Move Up"
                    >
                      ▲
                    </button>
                    <button
                      className="btn-icon small"
                      disabled={index === proposedPlan.ordered_stops.length - 1}
                      onClick={() => handleMoveStop(index, 1)}
                      title="Move Down"
                    >
                      ▼
                    </button>
                  </div>
                </div>

                {hasPerishable && (
                  <div className="rule-note perishable">
                    🧊 <strong>Freshness rule applied:</strong> Placed near the end of the trip so refrigerated items don't spoil.
                  </div>
                )}

                {isBanking && (
                  <div className="rule-note banking">
                    💵 <strong>Prerequisite rule applied:</strong> Scheduled first so you have cash on hand for other stops.
                  </div>
                )}

                <div className="stop-tasks-list">
                  <div className="tasks-label">Tasks at this stop:</div>
                  {stop.tasks.map((task, tIdx) => (
                    <div key={tIdx} className="stop-task-item">
                      <span className="task-bullet">•</span>
                      <span className="task-title">{task.title}</span>
                      {task.deadline && (
                        <span className="badge badge-deadline">⏰ {task.deadline}</span>
                      )}
                      {task.urgency === 'high' && (
                        <span className="badge badge-urgent">🔥 Urgent</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        <div className="plan-actions-footer">
          <button className="btn btn-secondary" onClick={onBackToInbox}>
            ← Back to Inbox
          </button>
          <button className="btn btn-primary pulse-btn" onClick={onProceedToDeparture}>
            Ready to Leave? (Pack Checklist) →
          </button>
        </div>
      </div>
    </div>
  );
}

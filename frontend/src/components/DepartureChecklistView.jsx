import React, { useState } from 'react';

export default function DepartureChecklistView({
  proposedPlan,
  onBackToPlan,
  onStartTrip,
}) {
  const [packingList, setPackingList] = useState(() => {
    return (proposedPlan?.departure_checklist || []).map((label) => ({
      label,
      checked: false,
    }));
  });

  const [customItem, setCustomItem] = useState('');
  const [tripName, setTripName] = useState('My Outdoor Errand Trip');
  const [isStarting, setIsStarting] = useState(false);

  const toggleCheck = (index) => {
    setPackingList((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], checked: !copy[index].checked };
      return copy;
    });
  };

  const handleAddCustom = (e) => {
    e.preventDefault();
    if (!customItem.trim()) return;
    setPackingList((prev) => [...prev, { label: customItem.trim(), checked: false }]);
    setCustomItem('');
  };

  const handleStart = async () => {
    setIsStarting(true);
    try {
      // Pass the updated checklist back into the plan
      const updatedPlan = {
        ...proposedPlan,
        departure_checklist: packingList.map((p) => p.label),
      };
      await onStartTrip(tripName, updatedPlan);
    } catch (err) {
      alert('Failed to start trip: ' + err.message);
    } finally {
      setIsStarting(false);
    }
  };

  const allPacked = packingList.length > 0 && packingList.every((p) => p.checked);

  return (
    <div className="view-container departure-view">
      <div className="section-card">
        <h2 className="section-title">
          <span>🎒</span> Ready to Leave? Departure Checklist
        </h2>
        <p className="section-subtitle">
          Don't forget anything before stepping out the door! Check off what you have in your bag.
        </p>

        <div className="trip-name-box">
          <label className="form-label">Trip Name</label>
          <input
            type="text"
            className="form-input"
            value={tripName}
            onChange={(e) => setTripName(e.target.value)}
          />
        </div>

        <div className="checklist-container">
          {packingList.map((item, idx) => (
            <label
              key={idx}
              className={`checklist-item ${item.checked ? 'packed' : ''}`}
            >
              <input
                type="checkbox"
                className="checklist-checkbox"
                checked={item.checked}
                onChange={() => toggleCheck(idx)}
              />
              <span className="checklist-text">{item.label}</span>
              {item.checked && <span className="packed-tag">✓ Packed</span>}
            </label>
          ))}
        </div>

        <form className="add-packing-form" onSubmit={handleAddCustom}>
          <input
            type="text"
            className="form-input"
            placeholder="Add another item to carry (e.g., umbrella, house keys)..."
            value={customItem}
            onChange={(e) => setCustomItem(e.target.value)}
          />
          <button type="submit" className="btn btn-secondary">
            + Add
          </button>
        </form>

        <div className="departure-footer">
          <button className="btn btn-secondary" onClick={onBackToPlan}>
            ← Adjust Stops
          </button>
          <button
            className={`btn btn-primary pulse-btn ${allPacked ? 'all-ready' : ''}`}
            onClick={handleStart}
            disabled={isStarting}
          >
            {isStarting ? 'Starting...' : '🚀 Step Outside & Start Trip'}
          </button>
        </div>
      </div>
    </div>
  );
}

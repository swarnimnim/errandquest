import React, { useState } from 'react';
import { parseErrandsText, createErrand, deleteErrand } from '../api';

const CATEGORIES = [
  'Groceries',
  'Printing & Stationery',
  'Parcel & Mail',
  'Pharmacy & Health',
  'Banking & Cash',
  'Personal Care',
  'Services & Repair',
  'General',
];

export default function InboxView({
  errands,
  onRefreshErrands,
  onProceedToPlan,
}) {
  const [nlInput, setNlInput] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [parsedPreview, setParsedPreview] = useState([]);
  const [showManualForm, setShowManualForm] = useState(false);

  // Manual task form state
  const [manualTitle, setManualTitle] = useState('');
  const [manualCategory, setManualCategory] = useState('General');
  const [manualUrgency, setManualUrgency] = useState('medium');
  const [manualDeadline, setManualDeadline] = useState('');

  const sampleTexts = [
    'Buy milk and vegetables, print my assignment, collect parcel before 5, get shampoo, and withdraw cash at ATM.',
    'Drop off laundry, buy cold flu tablets at chemist, and pick up Amazon package before 4 PM.',
    'Need milk too, and return library books by noon.',
  ];

  const handleParse = async () => {
    if (!nlInput.trim()) return;
    setIsParsing(true);
    try {
      const data = await parseErrandsText(nlInput);
      setParsedPreview(data.tasks || []);
    } catch (err) {
      alert('Failed to parse input: ' + err.message);
    } finally {
      setIsParsing(false);
    }
  };

  const handleConfirmAddPreview = async () => {
    if (parsedPreview.length === 0) return;
    try {
      for (const task of parsedPreview) {
        await createErrand({
          title: task.title,
          category: task.category || 'General',
          urgency: task.urgency || 'medium',
          deadline: task.deadline || null,
          prep_items: task.prep_items || [],
          status: 'pending',
        });
      }
      setParsedPreview([]);
      setNlInput('');
      onRefreshErrands();
    } catch (err) {
      alert('Error saving errands: ' + err.message);
    }
  };

  const handleManualAdd = async (e) => {
    e.preventDefault();
    if (!manualTitle.trim()) return;
    try {
      await createErrand({
        title: manualTitle.trim(),
        category: manualCategory,
        urgency: manualUrgency,
        deadline: manualDeadline.trim() || null,
        prep_items: ['Payment method'],
        status: 'pending',
      });
      setManualTitle('');
      setManualDeadline('');
      setShowManualForm(false);
      onRefreshErrands();
    } catch (err) {
      alert('Error adding errand: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteErrand(id);
      onRefreshErrands();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  const updatePreviewItem = (index, field, value) => {
    setParsedPreview((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], [field]: value };
      return copy;
    });
  };

  const removePreviewItem = (index) => {
    setParsedPreview((prev) => prev.filter((_, i) => i !== index));
  };

  const pendingErrands = errands.filter(
    (e) => e.status === 'pending' || e.status === 'carry_forward'
  );

  return (
    <div className="view-container inbox-view">
      <div className="section-card">
        <h2 className="section-title">
          <span>✍️</span> Capture Errands
        </h2>
        <p className="section-subtitle">
          Type everything you need to do in plain English. The AI will extract,
          categorize, and prepare them for your trip.
        </p>

        <div className="capture-box">
          <textarea
            className="nl-textarea"
            rows={3}
            placeholder="e.g. Buy 2L milk, print lab file, collect parcel before 5 PM, get shampoo, and withdraw cash at ATM..."
            value={nlInput}
            onChange={(e) => setNlInput(e.target.value)}
          />

          <div className="sample-prompts">
            <span className="sample-label">Try sample:</span>
            {sampleTexts.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="chip-btn"
                onClick={() => setNlInput(sample)}
              >
                Sample {idx + 1}
              </button>
            ))}
          </div>

          <div className="action-row">
            <button
              className="btn btn-primary"
              onClick={handleParse}
              disabled={isParsing || !nlInput.trim()}
            >
              {isParsing ? '⏳ Extracting...' : '✨ Extract with AI'}
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => setShowManualForm(!showManualForm)}
            >
              {showManualForm ? 'Hide Manual Form' : '➕ Add Single Task'}
            </button>
          </div>
        </div>

        {/* Manual Form Toggle */}
        {showManualForm && (
          <form className="manual-form" onSubmit={handleManualAdd}>
            <div className="form-group">
              <label>Task Title *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Buy eggs"
                value={manualTitle}
                onChange={(e) => setManualTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Category</label>
                <select
                  className="form-select"
                  value={manualCategory}
                  onChange={(e) => setManualCategory(e.target.value)}
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Urgency</label>
                <select
                  className="form-select"
                  value={manualUrgency}
                  onChange={(e) => setManualUrgency(e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High / Urgent</option>
                </select>
              </div>
              <div className="form-group">
                <label>Deadline (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. before 5 PM"
                  value={manualDeadline}
                  onChange={(e) => setManualDeadline(e.target.value)}
                />
              </div>
            </div>
            <button type="submit" className="btn btn-success">
              Save Errand to Inbox
            </button>
          </form>
        )}
      </div>

      {/* AI Parsed Tasks Preview Box (Step 2 in PRD) */}
      {parsedPreview.length > 0 && (
        <div className="section-card preview-card">
          <div className="preview-header">
            <h3>🔍 Review AI Extracted Tasks ({parsedPreview.length})</h3>
            <p>Verify or edit categories before saving to your inbox.</p>
          </div>

          <div className="preview-list">
            {parsedPreview.map((item, index) => (
              <div key={index} className="preview-item">
                {item.is_possible_duplicate && (
                  <div className="duplicate-alert">
                    ⚠️ <strong>Duplicate alert:</strong> You already have a similar errand (<em>"{item.duplicate_of}"</em>).
                  </div>
                )}
                <div className="preview-fields">
                  <input
                    type="text"
                    className="form-input"
                    value={item.title}
                    onChange={(e) => updatePreviewItem(index, 'title', e.target.value)}
                  />
                  <select
                    className="form-select"
                    value={item.category}
                    onChange={(e) => updatePreviewItem(index, 'category', e.target.value)}
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                  <select
                    className="form-select"
                    value={item.urgency}
                    onChange={(e) => updatePreviewItem(index, 'urgency', e.target.value)}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">Urgent</option>
                  </select>
                  <button
                    type="button"
                    className="btn-icon danger"
                    title="Remove"
                    onClick={() => removePreviewItem(index)}
                  >
                    🗑️
                  </button>
                </div>
                {item.deadline && (
                  <span className="badge badge-deadline">⏰ {item.deadline}</span>
                )}
                {item.prep_items && item.prep_items.length > 0 && (
                  <span className="badge badge-prep">
                    🎒 Carry: {item.prep_items.join(', ')}
                  </span>
                )}
              </div>
            ))}
          </div>

          <div className="preview-actions">
            <button className="btn btn-success" onClick={handleConfirmAddPreview}>
              ✓ Confirm & Add All to Inbox
            </button>
            <button className="btn btn-secondary" onClick={() => setParsedPreview([])}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Pending Errands Inbox */}
      <div className="section-card">
        <div className="list-header">
          <h2 className="section-title">
            <span>📦</span> Pending Errands ({pendingErrands.length})
          </h2>
          {pendingErrands.length > 0 && (
            <button
              className="btn btn-primary pulse-btn"
              onClick={onProceedToPlan}
            >
              🚀 Plan Trip Now ({pendingErrands.length})
            </button>
          )}
        </div>

        {pendingErrands.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🌱</div>
            <h3>Your Errand Inbox is Empty</h3>
            <p>Enter errands above to plan your next outing and save unnecessary trips!</p>
          </div>
        ) : (
          <div className="errand-list">
            {pendingErrands.map((errand) => (
              <div key={errand.id} className="errand-card">
                <div className="errand-main">
                  <div className="errand-title-row">
                    <span className="errand-title">{errand.title}</span>
                    {errand.status === 'carry_forward' && (
                      <span className="badge badge-carry">Carried Forward</span>
                    )}
                    {errand.urgency === 'high' && (
                      <span className="badge badge-urgent">🔥 Urgent</span>
                    )}
                  </div>
                  <div className="errand-meta">
                    <span className="category-pill">{errand.category}</span>
                    {errand.deadline && (
                      <span className="meta-item">⏰ {errand.deadline}</span>
                    )}
                    {errand.prep_items && errand.prep_items.length > 0 && (
                      <span className="meta-item">
                        🎒 {errand.prep_items.join(', ')}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  className="btn-icon danger"
                  title="Delete errand"
                  onClick={() => handleDelete(errand.id)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

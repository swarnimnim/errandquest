const BASE_URL = '/api';

export async function fetchAIStatus() {
  const res = await fetch(`${BASE_URL}/ai/status`);
  if (!res.ok) throw new Error('Failed to fetch AI status');
  return res.json();
}

export async function parseErrandsText(text) {
  const res = await fetch(`${BASE_URL}/errands/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error('Failed to parse errands');
  return res.json();
}

export async function fetchErrands(status) {
  const url = status ? `${BASE_URL}/errands?status=${encodeURIComponent(status)}` : `${BASE_URL}/errands`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch errands');
  return res.json();
}

export async function createErrand(errand) {
  const res = await fetch(`${BASE_URL}/errands`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(errand),
  });
  if (!res.ok) throw new Error('Failed to create errand');
  return res.json();
}

export async function updateErrand(id, updates) {
  const res = await fetch(`${BASE_URL}/errands/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update errand');
  return res.json();
}

export async function deleteErrand(id) {
  const res = await fetch(`${BASE_URL}/errands/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete errand');
  return res.json();
}

export async function planProposedTrip(errands = null) {
  const payload = errands ? { errands } : { use_pending_db: true };
  const res = await fetch(`${BASE_URL}/trips/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate trip plan');
  }
  return res.json();
}

export async function startNewTrip(name, plan) {
  const res = await fetch(`${BASE_URL}/trips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, plan }),
  });
  if (!res.ok) throw new Error('Failed to start trip');
  return res.json();
}

export async function fetchActiveTrip() {
  const res = await fetch(`${BASE_URL}/trips/active`);
  if (!res.ok) throw new Error('Failed to fetch active trip');
  return res.json();
}

export async function updateTripItem(tripId, itemId, completed) {
  const res = await fetch(`${BASE_URL}/trips/${tripId}/items/${itemId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed }),
  });
  if (!res.ok) throw new Error('Failed to update trip item');
  return res.json();
}

export async function updatePackingItem(tripId, packingId, checked) {
  const res = await fetch(`${BASE_URL}/trips/${tripId}/packing/${packingId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ checked }),
  });
  if (!res.ok) throw new Error('Failed to update packing item');
  return res.json();
}

export async function completeTrip(tripId) {
  const res = await fetch(`${BASE_URL}/trips/${tripId}/complete`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to complete trip');
  return res.json();
}

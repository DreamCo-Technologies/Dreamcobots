(() => {
  const $ = id => document.getElementById(id);
  const storageKey = 'dreamco.buddy.world-lens.waypoints.v1';
  let current = null;
  let watchId = null;

  const readWaypoints = () => {
    try { return JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch { return []; }
  };
  const escapeHtml = value => String(value).replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
  const coordinate = value => Number(value).toFixed(6);
  const freshness = timestamp => {
    const seconds = Math.max(0, Math.round((Date.now() - timestamp) / 1000));
    return seconds < 5 ? 'just now' : `${seconds}s old`;
  };
  const setStatus = (message, good = false) => {
    $('lens-status').textContent = message;
    $('lens-status').style.color = good ? '#65d3a3' : '#e5c66f';
  };

  function plotPoint(latitude, longitude, className, label) {
    const point = document.createElement('button');
    point.className = className;
    point.type = 'button';
    point.title = label;
    point.setAttribute('aria-label', label);
    point.style.left = `${((longitude + 180) / 360) * 100}%`;
    point.style.top = `${((90 - latitude) / 180) * 100}%`;
    $('lens-map').append(point);
  }

  function render() {
    $('lens-map').querySelectorAll('.lens-point').forEach(point => point.remove());
    const waypoints = readWaypoints();
    for (const item of waypoints) plotPoint(item.latitude, item.longitude, 'lens-point', item.name);
    $('lens-waypoints').innerHTML = waypoints.length ? waypoints.map(item => `<article class="lens-item"><strong>${escapeHtml(item.name)}</strong><div>${coordinate(item.latitude)}, ${coordinate(item.longitude)}</div><div>${escapeHtml(item.note || 'No note')} · ${escapeHtml(item.source)}</div></article>`).join('') : '<p>No waypoints saved.</p>';
  }

  function acceptPosition(position) {
    current = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracyMeters: position.coords.accuracy,
      altitudeMeters: position.coords.altitude,
      headingDegrees: position.coords.heading,
      speedMetersPerSecond: position.coords.speed,
      timestamp: position.timestamp,
      source: 'browser_geolocation'
    };
    $('lens-latitude').textContent = coordinate(current.latitude);
    $('lens-longitude').textContent = coordinate(current.longitude);
    $('lens-accuracy').textContent = `${Math.round(current.accuracyMeters)} m`;
    $('lens-freshness').textContent = freshness(current.timestamp);
    $('lens-cross').hidden = false;
    $('lens-readout').textContent = `DEVICE GPS · ${coordinate(current.latitude)}, ${coordinate(current.longitude)} · accuracy ±${Math.round(current.accuracyMeters)}m · ${freshness(current.timestamp)}`;
    setStatus(`GPS fix received with ±${Math.round(current.accuracyMeters)} meter reported accuracy.`, true);
  }

  function locationError(error) {
    const labels = {1: 'Location permission was denied.', 2: 'Your position is unavailable.', 3: 'The GPS request timed out.'};
    setStatus(labels[error.code] || 'Buddy could not read the device location.');
  }

  function requireGeolocation(callback) {
    if (!navigator.geolocation) { setStatus('This browser does not provide the Geolocation API.'); return; }
    setStatus('Requesting browser location permission…');
    callback();
  }

  $('lens-locate').addEventListener('click', () => requireGeolocation(() => navigator.geolocation.getCurrentPosition(acceptPosition, locationError, { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 })));
  $('lens-watch').addEventListener('click', () => requireGeolocation(() => {
    if (watchId !== null) return;
    watchId = navigator.geolocation.watchPosition(acceptPosition, locationError, { enableHighAccuracy: true, timeout: 15000, maximumAge: 3000 });
    $('lens-watch').disabled = true;
    $('lens-stop').disabled = false;
    setStatus('Live GPS started by you. Use Stop when finished.', true);
  }));
  $('lens-stop').addEventListener('click', () => {
    if (watchId !== null) navigator.geolocation.clearWatch(watchId);
    watchId = null;
    $('lens-watch').disabled = false;
    $('lens-stop').disabled = true;
    setStatus('Live GPS stopped. The last fix remains visible locally.');
  });

  $('lens-add').addEventListener('click', () => {
    const manualLatitude = $('lens-manual-lat').value.trim();
    const manualLongitude = $('lens-manual-lon').value.trim();
    const latitude = manualLatitude === '' ? current?.latitude : Number(manualLatitude);
    const longitude = manualLongitude === '' ? current?.longitude : Number(manualLongitude);
    const name = $('lens-name').value.trim();
    if (!name) { setStatus('Give the waypoint a name first.'); return; }
    if (!Number.isFinite(latitude) || latitude < -90 || latitude > 90 || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) { setStatus('Enter valid coordinates or request a GPS fix first.'); return; }
    const items = readWaypoints();
    items.push({ id: `waypoint-${Date.now()}`, name, note: $('lens-note').value.trim(), latitude, longitude, source: manualLatitude === '' ? 'owner_approved_device_gps' : 'owner_entered_coordinates', recordedAt: new Date().toISOString() });
    localStorage.setItem(storageKey, JSON.stringify(items.slice(-100)));
    $('lens-name').value = '';
    $('lens-note').value = '';
    render();
    setStatus('Waypoint saved in this browser only.', true);
  });

  $('lens-export').addEventListener('click', () => {
    const packet = { schema: 'dreamco.buddy.spatial_mission_packet.v1', createdAt: new Date().toISOString(), safety: 'Not for navigation, emergencies, surveillance, or tracking people.', waypoints: readWaypoints() };
    const url = URL.createObjectURL(new Blob([JSON.stringify(packet, null, 2)], { type: 'application/json' }));
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'buddy-world-lens-mission.json'; anchor.click(); URL.revokeObjectURL(url);
    setStatus('Mission packet exported. No network upload occurred.', true);
  });
  $('lens-clear').addEventListener('click', () => {
    localStorage.removeItem(storageKey);
    render();
    setStatus('Local waypoint data cleared.');
  });
  $('lens-buddy').addEventListener('click', () => {
    const command = $('lens-command').value.trim();
    if (!command) { setStatus('Describe what Buddy should do with these waypoints.'); return; }
    const spatialContext = readWaypoints().map(({name, note, latitude, longitude, source}) => ({name, note, latitude, longitude, source}));
    const prompt = `${command}\n\nOwner-provided World Lens context: ${JSON.stringify(spatialContext)}\nTreat coordinates as private, possibly inaccurate context. Do not infer or track people. Do not present output as safety-critical navigation.`;
    location.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
  });
  window.addEventListener('pagehide', () => { if (watchId !== null) navigator.geolocation.clearWatch(watchId); });
  render();
})();

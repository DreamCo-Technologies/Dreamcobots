(() => {
  const $ = id => document.getElementById(id);
  const storageKey = 'dreamco.buddy.world-lens.waypoints.v1';
  const peopleKey = 'dreamco.buddy.world-lens.people.v1';
  let current = null;
  let watchId = null;
  let lastPropertyScan = 0;

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
    if ($('lens-external-map').checked) refreshExternalMap();
    if (watchId !== null && $('lens-property-auto').checked && Date.now() - lastPropertyScan > 30000) void queryProperties();
  }

  function refreshExternalMap() {
    if (!$('lens-external-map').checked) { setStatus('Approve external map requests before loading the map.'); return; }
    if (!current) { setStatus('Request a GPS fix before loading the external map.'); return; }
    const span = 0.012;
    const bbox = [current.longitude-span,current.latitude-span,current.longitude+span,current.latitude+span].join(',');
    $('lens-map-frame').src = `https://www.openstreetmap.org/export/embed.html?bbox=${encodeURIComponent(bbox)}&layer=mapnik&marker=${encodeURIComponent(`${current.latitude},${current.longitude}`)}`;
    $('lens-map-frame').hidden = false;
    setStatus('External OpenStreetMap request enabled for this session.', true);
  }

  const safeText = value => escapeHtml(value ?? 'Not supplied');
  async function queryProperties() {
    if (!current) { $('lens-property-status').textContent = 'Request a GPS fix first.'; return; }
    const endpoint = $('lens-property-endpoint').value.trim();
    if (!/^https:\/\//i.test(endpoint)) { $('lens-property-status').textContent = 'Connect an authorized HTTPS listing endpoint first.'; return; }
    localStorage.setItem('dreamco.buddy.world-lens.property-endpoint.v1', endpoint);
    const url = new URL(endpoint);
    url.searchParams.set('lat', current.latitude);
    url.searchParams.set('lon', current.longitude);
    url.searchParams.set('radiusMeters', '500');
    $('lens-property-status').textContent = 'Checking the connected provider…';
    lastPropertyScan = Date.now();
    try {
      const response = await fetch(url, { headers: { Accept: 'application/json' }, credentials: 'omit' });
      if (!response.ok) throw new Error(`provider returned ${response.status}`);
      const payload = await response.json();
      const listings = Array.isArray(payload) ? payload : (payload.listings || payload.value || []);
      $('lens-properties-list').innerHTML = listings.slice(0, 50).map(item => `<article class="lens-item"><strong>${safeText(item.address || item.UnparsedAddress)}</strong><div>${safeText(item.price || item.ListPrice)} · ${safeText(item.bedrooms || item.BedroomsTotal)} beds · ${safeText(item.bathrooms || item.BathroomsTotalInteger)} baths</div><div>${safeText(item.status || item.StandardStatus)} · ${safeText(item.source || 'connected provider')}</div></article>`).join('') || '<p>No nearby listings returned.</p>';
      $('lens-property-status').textContent = `${listings.length} provider listing${listings.length === 1 ? '' : 's'} returned. Verify before investing.`;
    } catch (error) { $('lens-property-status').textContent = `Property request failed: ${error.message}`; }
  }

  function renderPeople() {
    let people = [];
    try { people = JSON.parse(localStorage.getItem(peopleKey) || '[]'); } catch {}
    $('lens-people').innerHTML = people.length ? people.map(person => `<article class="lens-item">${person.photo ? `<img src="${person.photo}" alt="User-selected profile for ${safeText(person.name)}" style="width:48px;height:48px;object-fit:cover;border-radius:50%;float:left;margin-right:10px">` : ''}<strong>${safeText(person.name)}</strong><div>${safeText(person.relationship)}</div><div>${safeText(person.notes)}</div><div>${safeText(person.sharedLocation || 'No shared location')} · consent recorded ${safeText(person.consentRecordedAt)}</div><div style="clear:both"></div></article>`).join('') : '<p>No consented profiles saved.</p>';
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
  $('lens-map-refresh').addEventListener('click', refreshExternalMap);
  $('lens-properties').addEventListener('click', () => void queryProperties());
  $('lens-person-save').addEventListener('click', () => {
    const name = $('lens-person-name').value.trim();
    if (!name || !$('lens-person-consent').checked) { setStatus('A name and the person’s informed consent are required.'); return; }
    const location = $('lens-person-location').value.trim();
    if (location && !/^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(location)) { setStatus('Shared location must use latitude, longitude.'); return; }
    const save = photo => {
      let people = []; try { people = JSON.parse(localStorage.getItem(peopleKey) || '[]'); } catch {}
      people.push({ id:`person-${Date.now()}`, name, relationship:$('lens-person-relationship').value.trim(), notes:$('lens-person-notes').value.trim(), sharedLocation:location, photo, consentRecordedAt:new Date().toISOString(), consent:true });
      localStorage.setItem(peopleKey, JSON.stringify(people.slice(-50))); renderPeople(); setStatus('Consented profile saved locally. No face recognition was performed.', true);
    };
    const file = $('lens-person-photo').files[0];
    if (!file) { save(''); return; }
    if (file.size > 1_000_000) { setStatus('Choose a profile photo smaller than 1 MB.'); return; }
    const reader = new FileReader(); reader.onload = () => save(String(reader.result)); reader.readAsDataURL(file);
  });
  $('lens-person-clear').addEventListener('click', () => { localStorage.removeItem(peopleKey); renderPeople(); setStatus('All locally saved people profiles were revoked and cleared.'); });
  $('lens-property-endpoint').value = localStorage.getItem('dreamco.buddy.world-lens.property-endpoint.v1') || '';
  window.addEventListener('pagehide', () => { if (watchId !== null) navigator.geolocation.clearWatch(watchId); });
  render();
  renderPeople();
})();

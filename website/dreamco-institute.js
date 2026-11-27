const CATALOG_URL = "../config/dreamco-institute-academic-catalog.json";
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
let catalog;

function renderColleges() {
  $("#college-count").textContent = catalog.colleges.length;
  $("#division-count").textContent = catalog.division_crosswalk.domain_division_count;
  $("#college-grid").innerHTML = catalog.colleges.map((college) => {
    const count = catalog.division_crosswalk.academic_assignments.filter((row) => row.academic_college_id === college.id).length;
    return `<article class="college-card"><span class="college-code">${esc(college.code)} · ACADEMIC COLLEGE</span><h3>${esc(college.name)}</h3><p>${esc(college.mission)}</p><p class="dean">${esc(college.dean)}</p><p class="division-count">${count} domain academic homes · ${college.courses.length} catalog courses</p></article>`;
  }).join("");
  $("#college-filter").innerHTML = '<option value="all">All colleges</option>' + catalog.colleges.map((college) => `<option value="${esc(college.id)}">${esc(college.name)}</option>`).join("");
}

function renderCourses() {
  const collegeId = $("#college-filter").value;
  const query = $("#course-search").value.trim().toLowerCase();
  const courses = catalog.colleges.flatMap((college) => college.courses.map((course) => ({...course, college})))
    .filter((course) => (collegeId === "all" || course.college.id === collegeId))
    .filter((course) => `${course.code} ${course.title} ${course.college.name}`.toLowerCase().includes(query));
  $("#course-list").innerHTML = courses.length ? courses.map((course) => `<article class="course-card"><div class="course-meta"><span>${esc(course.code)}</span><span>${course.credits} CREDITS · LEVEL ${course.level}</span></div><h3>${esc(course.title)}</h3><p>${esc(course.college.name)}</p><p><strong>Laboratory practicum:</strong> ${esc(course.practicum)}</p><ul>${course.outcomes.map((outcome) => `<li>${esc(outcome)}</li>`).join("")}</ul></article>`).join("") : "<p>No courses match that search.</p>";
}

function renderTranscript(transcript) {
  if (!transcript || transcript.schema !== "dreamco.institute.transcript.v1") throw new Error("This file is not a DreamCo Institute transcript.");
  const summary = transcript.summary || {};
  const rows = Array.isArray(transcript.academic_record) ? transcript.academic_record : [];
  $("#transcript-view").innerHTML = `<div class="transcript-head"><div><h3>${esc(transcript.institution)}</h3><p>${esc(transcript.candidate_id)} · ${esc(transcript.college?.name)}</p></div><div class="status-line">${summary.graduated ? "INTERNAL CREDENTIAL CONFERRED" : "ACADEMIC RECORD IN PROGRESS"}</div></div><div class="transcript-stats"><div class="transcript-stat"><strong>${esc(summary.credits_earned ?? 0)} / ${esc(summary.credits_required ?? 0)}</strong><span>Credits earned</span></div><div class="transcript-stat"><strong>${esc(summary.cumulative_gpa ?? "—")}</strong><span>Cumulative GPA</span></div><div class="transcript-stat"><strong>${esc(summary.academic_standing ?? "—")}</strong><span>Academic standing</span></div><div class="transcript-stat"><strong>${transcript.capstone?.passed ? "Passed" : "Pending"}</strong><span>Thesis defense</span></div></div><table class="transcript-table"><thead><tr><th>Course</th><th>Credits</th><th>Grade</th><th>Practicum</th><th>Holdout</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.course_code)} · ${esc(row.course_title)}</td><td>${esc(row.credits_earned)}/${esc(row.credits_attempted)}</td><td>${esc(row.letter_grade)}</td><td>${row.practicum_passed ? "Passed" : "Not passed"}</td><td>${row.independent_holdout_passed ? "Passed" : "Not passed"}</td></tr>`).join("")}</tbody></table><p class="credential-note">Registrar checksum: ${esc(transcript.registrar_seal_sha256 || "not supplied")}. This portal displays the checksum but does not cryptographically authenticate the issuer. ${esc(transcript.accreditation_disclaimer || "")}</p>`;
}

async function init() {
  try {
    const response = await fetch(CATALOG_URL);
    if (!response.ok) throw new Error(`Academic catalog request failed: HTTP ${response.status}`);
    catalog = await response.json();
    if (catalog.schema !== "dreamco.institute.academic_catalog.v1") throw new Error("Unsupported academic catalog schema.");
    renderColleges();
    renderCourses();
    $("#college-filter").addEventListener("change", renderCourses);
    $("#course-search").addEventListener("input", renderCourses);
  } catch (error) {
    $("#college-grid").textContent = error.message;
    $("#transcript-status").textContent = "Academic catalog unavailable.";
  }
  $("#transcript-file").addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const transcript = JSON.parse(await file.text());
      renderTranscript(transcript);
      $("#transcript-status").textContent = `Loaded ${file.name}. Display only; issuer authenticity is not established by this page.`;
    } catch (error) {
      $("#transcript-status").textContent = `Transcript not loaded: ${error.message}`;
    }
  });
}
init();

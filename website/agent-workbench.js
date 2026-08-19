(function () {
  'use strict';
  const host = document.getElementById('agent-workbench');
  if (!host) return;
  fetch('data/buddy-actions-agent-workbench.json')
    .then((response) => { if (!response.ok) throw new Error(`Agent registry returned ${response.status}`); return response.json(); })
    .then((registry) => {
      host.replaceChildren();
      registry.agents.forEach((agent) => {
        const card = document.createElement('article');
        card.className = 'agent-workbench-card';
        const title = document.createElement('h3'); title.textContent = agent.name;
        const purpose = document.createElement('p'); purpose.textContent = agent.purpose;
        const evidence = document.createElement('p'); evidence.className = 'agent-workbench-evidence'; evidence.textContent = `Success: ${agent.success}`;
        const button = document.createElement('a'); button.className = 'btn btn-primary'; button.textContent = agent.primary_action;
        const prompt = `Act as Buddy's ${agent.name} specialist. ${agent.purpose} For the current repository/task, determine whether this specialist is the best choice for the next step using exact-task benchmark evidence, correctness, quality, reliability, speed, repository familiarity, cost, safety, permissions and recent regressions. Explain the recommendation before any consequential action. Success condition: ${agent.success}`;
        button.href = `buddy.html?prompt=${encodeURIComponent(prompt)}`;
        const learn = document.createElement('button'); learn.className = 'btn btn-outline'; learn.type = 'button'; learn.textContent = 'Why this agent?';
        learn.addEventListener('click', () => {
          const note = document.createElement('p'); note.className = 'agent-workbench-note'; note.textContent = `Buddy will compare this specialist with other candidates for the current step. It does not automatically mean this agent is best for the whole task. ${registry.selection_policy.reselect_when_task_changes ? 'Buddy re-evaluates when the task changes.' : ''}`;
          card.appendChild(note);
          learn.disabled = true;
        });
        const actions = document.createElement('div'); actions.className = 'agent-workbench-actions'; actions.append(button, learn);
        card.append(title, purpose, evidence, actions);
        host.appendChild(card);
      });
      const status = document.getElementById('agent-workbench-status');
      if (status) status.textContent = `${registry.agents.length} specialist roles ready. Buddy selects per step; it does not blindly use one agent for an entire job.`;
    })
    .catch((error) => {
      host.textContent = `Specialist registry unavailable: ${error.message}`;
    });
})();

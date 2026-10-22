"use strict";
const base="https://github.com/DreamCo-Technologies/Dreamcobots/blob/codex/task-model-taxonomy-20261022/";
const items=[
["Genealogy","buddy/genealogy_gedcom.py","Limited offline GEDCOM individual parser","Tests execution, relationships, UI, database and live record integrations"],
["Genealogy tests","tests/test_buddy_genealogy_gedcom.py","Six test cases committed","Run in CI and publish results"],
["Genealogy curriculum","config/buddy-genealogy-curriculum.json","Family history and genetic genealogy study requirements","Ingestion and measured learning"],
["Science / hardware / space","config/buddy-science-hardware-space-curriculum.json","Science, electronics, botany and space curriculum","Simulation and independent domain benchmarks"],
["DNA and business","config/buddy-dna-autonomous-business-curriculum.json","Genomics and ethical autonomous business curriculum","Working integrations and verified revenue"],
["Education sources","config/buddy-learning-sources.json","Learning-source registry and rights checks","Authorized video/transcript retrieval and mastery tests"],
["Biometric vault","buddy/biometric_vault.py","Encrypted template storage prototype","Managed keys, revocation across services, backup deletion, recognition adapters"],
["Community profiles","buddy/community_profiles.py","Opt-in profile metadata and greeting prototype","Secure verified-identity boundary and enrollment interface"],
["Inbox / workflow controls","buddy/inbox_workflow_policy.py","Account-scoped authorization and dry-run planning","Dedicated mailbox, OAuth integration, live dispatch and tests"]
];
const tbody=document.getElementById("rows");
for(const [name,path,done,remaining] of items){
const tr=document.createElement("tr");
for(const value of [name,done,remaining]){const td=document.createElement("td");td.textContent=value;tr.appendChild(td);}
const link=document.createElement("a");link.href=base+path;link.textContent=" View source";link.rel="noopener noreferrer";tr.cells[1].appendChild(link);tbody.appendChild(tr);
}

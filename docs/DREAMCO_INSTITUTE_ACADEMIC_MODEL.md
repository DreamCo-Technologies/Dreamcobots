# DreamCo Institute of Autonomous Systems

## Institutional identity

DreamCo Institute of Autonomous Systems is the collegiate academic presentation for DreamCo's existing Buddy learning, evaluation, sandbox, provenance and Model Foundry systems. It is an institutional product identity, not a claim of government accreditation or professional licensure.

## Academic organization

The five colleges are Cognitive & Algorithmic Sciences (CS), Autonomous Robotics & Physical Systems (ROBO), Systems Security & Trust Governance (GOV), Human-Machine Interaction & Design (HMI), and Autonomous Enterprise & Operations (OPS).

The catalog maps the canonical 55 domain divisions to academic homes while preserving the separate 65-MasterBot registry. Academic placement is for curriculum navigation only. It does not modify operational ownership or approve any unresolved MasterBot-to-domain mapping in the canonical crosswalk.

## Credit and credential policy

A course credit requires a recorded assessment evidence identifier, a passed laboratory practicum, a passed independent holdout, and a grade of C or better. A college credential requires every required course credit, a cumulative GPA of at least 3.0, an independently reviewed capstone thesis, a passed oral defense, and a registrar review identifier.

The registrar emits an internal DreamCo credential only. The transcript's SHA-256 checksum detects accidental or malicious content changes but is not a digital signature, issuer authentication, or legal proof of authorship. A production registrar must bind issuance to authenticated identity, role-based authorization, an append-only audit record, key-backed digital signatures and revocation status before treating a credential as externally verifiable.

## Integration boundaries

The portal reads the academic catalog and a user-selected transcript JSON file. It does not write grades, run assessments, train models, update weights, execute robotic actions, or claim accreditation. Existing Buddy Bootcamp, professional training, authorized-source manifests, 65-MasterBot registry and Model Foundry remain canonical execution systems.

## Verification

Run:

```bash
python -m unittest tests.test_dreamco_institute_registrar -v
```

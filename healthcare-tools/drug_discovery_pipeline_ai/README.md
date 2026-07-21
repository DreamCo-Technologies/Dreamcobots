# Drug Discovery Pipeline AI

Computational drug discovery screening: Lipinski Rule-of-Five, ADMET prediction, and docking scores.

**DISCLAIMER:** All predictions are computational estimates and require experimental validation.

## Tiers
- **Free** ($0/mo): Compound lookup, basic property screening
- **Pro** ($199/mo): ADMET prediction, target docking score, lead optimization hints
- **Enterprise** ($999/mo): Multi-target screening, patent check, API access

## Usage
```python
import sys
sys.path.insert(0, "healthcare-tools/drug_discovery_pipeline_ai")
from drug_discovery_pipeline_ai import DrugDiscoveryPipelineAI

pipeline = DrugDiscoveryPipelineAI(tier="pro")
result = pipeline.screen_compound({"name": "Aspirin", "molecular_weight": 180, "logp": 1.2,
                                   "h_bond_donors": 1, "h_bond_acceptors": 4})
```

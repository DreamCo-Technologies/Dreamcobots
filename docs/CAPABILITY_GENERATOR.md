# Capability generator

`buddy/learning/capability_generator.py` writes one package for every dimension in `config/model-prospectus-benchmark-contract.json`. That matrix is the set used to compare Buddy with other models.

A generated file is cataloged. `evidence` stays empty, and the coverage report keeps `mastered` at 0. Having the package does not mean Buddy can do the task.

Run it with:

```bash
python3 buddy/learning/capability_generator.py
```

It writes `capabilities/generated/*.capability.json` and `config/generated/capability-coverage.json`. Re-run it when the reference matrix gains a dimension.

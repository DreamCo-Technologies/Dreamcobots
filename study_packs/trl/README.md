# study_packs/trl: TRL SFT / DPO / GRPO recipe pack

**Status: plan_only. No training has been run, and `trained_weights_exist: false`.**

This folder has templates for three training stages with Hugging Face TRL (target version 1.14.0):

- `recipes/sft.yaml` for supervised fine-tuning (`SFTConfig` and `SFTTrainer`)
- `recipes/dpo.yaml` for preference tuning from the SFT checkpoint (`DPOConfig` and `DPOTrainer`)
- `recipes/grpo.yaml` for reward-based RL from the SFT checkpoint (`GRPOConfig` and `GRPOTrainer`)

All three use LoRA through PEFT.

## Gates
`scripts/train_*.py` refuse to run unless `APPROVED_RUN=1` is set and every gate in `gates.json` is `green` with evidence attached. The gates are the base-model license, the dataset license, an eval baseline taken before training, a compute and cost estimate, a review of the GRPO reward function, and owner sign-off.

## Usage
    python scripts/train_sft.py --dry-run   # validates the config and prints the plan

## Links
This pack extends `docs/HUGGINGFACE_MASTERY_PLAN.md`, `config/huggingface-capability-packs.json`, and `config/huggingface-two-week-study.json` in DreamCo-Technologies/Dreamcobots. The model and dataset names are placeholders until the license gates pass.

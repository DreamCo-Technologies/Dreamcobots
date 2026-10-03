from _common import parse, lora, dataset
cfg = parse("dpo")
from trl import DPOConfig, DPOTrainer
DPOTrainer(model=cfg["base_model"], args=DPOConfig(**cfg["trainer_args"]),
           train_dataset=dataset(cfg), peft_config=lora(cfg)).train()

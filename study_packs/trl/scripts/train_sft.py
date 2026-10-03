from _common import parse, lora, dataset
cfg = parse("sft")
from trl import SFTConfig, SFTTrainer
SFTTrainer(model=cfg["base_model"], args=SFTConfig(**cfg["trainer_args"]),
           train_dataset=dataset(cfg), peft_config=lora(cfg)).train()

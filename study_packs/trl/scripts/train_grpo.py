from _common import parse, lora, dataset
cfg = parse("grpo")
from trl import GRPOConfig, GRPOTrainer
from rewards import format_reward
GRPOTrainer(model=cfg["base_model"], reward_funcs=[format_reward],
            args=GRPOConfig(**cfg["trainer_args"]),
            train_dataset=dataset(cfg), peft_config=lora(cfg)).train()

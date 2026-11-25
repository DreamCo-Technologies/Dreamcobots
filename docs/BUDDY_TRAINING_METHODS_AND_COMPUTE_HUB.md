# Buddy Training Methods and Compute Hub

## Purpose
The hub is a read-only catalog of training mechanisms and compute options. It helps users understand which method changes retrieval knowledge, adapters, tokenizers, or model weights, and which local, free-limited, framework, or paid compute options may be relevant.

## Methods
- Retrieval/RAG and skill packs: use authorized content without changing model weights.
- Prompting: inference-time instructions/examples, no weight update.
- SFT, LoRA, QLoRA, DPO, GRPO, distillation, continued pretraining, embedding/reward-model training, and full fine-tuning: weight or adapter-changing methods that require dataset rights, owner approval, and model/teacher license review.
- Tokenizer training: creates a tokenizer artifact and requires source-content rights and owner approval; it does not by itself prove a model was trained.
- Evaluation: measures capability without training.

## Compute options
Discovery options include local CPU/GPU hardware, limited free Colab/Kaggle resources, Hugging Face services, open training frameworks (PyTorch, Unsloth, Axolotl), and variable-price hosted compute (RunPod, Vast, Modal, AWS, Google Cloud, Azure). These are categories and documentation links, not a live availability or pricing quote.

The hub reports `availability_verified: false` and `price_verified: false` for every provider. A zero-dollar budget lists only local/existing and free-limited options. A positive budget expands discovery but does not purchase compute, create an account, or send a paid request.

## Approval and execution truth
A source-based method is eligible for review only when content rights and owner approval are verified. Weight-changing methods additionally require model-license verification. The hub never starts training, purchases compute, uploads data, or claims a checkpoint. Actual execution requires a separate approved job manifest, rights-cleared dataset, pinned model/tokenizer, compute authorization, worker, and evaluation receipts.

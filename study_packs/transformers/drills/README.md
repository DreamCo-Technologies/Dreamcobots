# Transformers core drills: concept notes

## 1. `pipeline()` — `tc.pipeline.pinned_textgen`
A pipeline bundles tokenizer, model, pre- and post-processing for one task. Always pass `model=` and
`revision=` (a bare task name picks a default model that can change). `device=-1` is CPU. Pass a list
to batch. For text generation, `return_full_text=False` returns only the new text.

## 2. `Auto*` classes — `tc.auto.load_pinned`
`AutoConfig` reads `config.json` and picks the architecture (`model_type`). `AutoTokenizer` and
`AutoModelForCausalLM` resolve the concrete classes from it. Safe defaults: `revision=<sha>`,
`use_safetensors=True`, `trust_remote_code=False`. A causal LM forward pass returns logits shaped
`(batch, seq_len, vocab_size)`; padding a batch needs a pad token.

## 3. `generate()` — `tc.generate.controls`
Greedy (`do_sample=False`) picks the argmax each step. Sampling (`do_sample=True`) uses
`temperature`, `top_p`, `top_k`, and is reproducible only with a fixed seed. `max_new_tokens` caps new
tokens (prefer it over `max_length`). A `GenerationConfig` object groups these settings; do not mix it
with loose kwargs (newer versions warn). Set `pad_token_id` when the model has none.
`TextIteratorStreamer` yields text as it is produced from a background thread. Determinism caveat: see
the CARD lesson about CPU threads.

## 4. Chat templates — `tc.chat_template.render`
`tokenizer.chat_template` is a Jinja template that turns a list of `{"role", "content"}` messages into
the exact string the model was trained on. `add_generation_prompt=True` appends the assistant header so
the model answers instead of continuing the user turn. `tokenize=False` returns the string,
`tokenize=True` returns ids (already containing special tokens, so do not re-add them), and
`return_dict=True` gives `input_ids` plus `attention_mask` ready for `generate()`.
`continue_final_message=True` leaves the last assistant turn open for prefill.

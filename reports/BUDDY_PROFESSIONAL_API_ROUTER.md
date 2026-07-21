# Buddy Professional API Router

Route every Buddy task to the best available model/resource with free-first defaults, user choice, fallbacks, safety gates, and cost controls.

## Modes

- free_first: Use local, open, and free-tier resources before any paid provider.
- local_only: Use only local/offline/open runtime resources.
- premium_optional: Use free routes first, then allow approved paid providers for hard tasks.
- quality_first: Use highest-quality approved provider route after user budget approval.

## Approval Required

- paid model calls
- provider key creation or rotation
- uploading private user media
- customer data processing by third-party providers
- voice or likeness cloning
- production route changes
- public claims that one model is best without current eval evidence

## Sample Routes

- general_chat: llama-3.1-8b-instruct -> qwen2.5-7b-instruct, mistral-7b-instruct, gemma-2-2b-it, gemma-2-9b-it
- coding: qwen2.5-32b-instruct -> qwen2.5-coder-7b, qwen2.5-coder-14b, deepseek-coder-6.7b-instruct, deepseek-coder-v2-lite
- debugging: qwen2.5-coder-7b -> qwen2.5-coder-32b, deepseek-coder-6.7b-instruct, command-r, command-r-plus
- repo_review: qwen2.5-coder-14b -> llama-3.2-vision-11b, llama-3.3-70b-instruct, deepseek-coder-v2-lite, codegemma-7b-it
- tool_building: qwen2.5-coder-14b -> deepseek-coder-v2-lite, codegemma-7b-it, segment-anything, langchain
- api_router_design: stable-diffusion-3-medium -> command-r, command-r-plus, cloudflare-workers-free, llama-3.1-8b-instruct
- workflow_automation: mixtral-8x7b-instruct -> langchain, autogen, crewai, command-r
- customer_support: llama-3.1-8b-instruct -> mistral-nemo-instruct, deepseek-r1-distill-llama-70b, command-r, command-r-plus
- sales_copy: command-r -> command-r-plus, llama-3.1-8b-instruct, llama-3.1-70b-instruct, llama-3.2-vision-11b
- business_strategy: llama-3.1-70b-instruct -> qwen2.5-72b-instruct, crewai, command-r, command-r-plus
- market_research: command-r-plus -> stable-diffusion-xl, command-r, llama-3.1-8b-instruct, llama-3.1-70b-instruct
- competitor_analysis: mixtral-8x22b-instruct -> qwen2.5-14b-instruct, qwen2.5-72b-instruct, gemma-2-27b-it, yi-1.5-34b-chat
- lead_research_packet: command-r-plus -> command-r, llama-3.1-8b-instruct, llama-3.1-70b-instruct, llama-3.2-vision-11b
- grant_contract_research: command-r-plus -> command-r, llama-3.1-8b-instruct, llama-3.1-70b-instruct, llama-3.2-vision-11b
- document_summary: llama-3.2-vision-11b -> tesseract-ocr, layoutlmv3, donut-base, nougat
- legal_safety_review: llama-3.2-vision-11b -> llama-3.3-70b-instruct, qwen2.5-coder-14b, codegemma-7b-it, command-r
- financial_analysis_draft: mixtral-8x22b-instruct -> qwen2.5-14b-instruct, qwen2.5-72b-instruct, gemma-2-2b-it, gemma-2-27b-it
- data_extraction: duckdb -> nougat, command-r, command-r-plus, supabase-free
- dashboard_building: qwen2.5-coder-14b -> command-r, command-r-plus, llama-3.1-8b-instruct, llama-3.1-70b-instruct
- spreadsheet_analysis: duckdb -> mixtral-8x22b-instruct, qwen2.5-14b-instruct, qwen2.5-72b-instruct, gemma-2-27b-it

# Buddy AI Agent Model Library Report

Give Buddy a governed prompt, tool, agent, and model-resource library so every bot can pick the best AI route for each task, explain tradeoffs, and fall back safely.

## Summary

- Model resources: 104
- Target model resources: 100
- Top 100 model resources ready: True
- Providers: 23
- Low-cost resources: 86
- Google Gemini resources: 8
- Free or cheap routing enabled: True
- Agent types: 18
- World model council ready: True
- World model council steps: 7
- Benchmark sources: 5
- Training/eval policy ready: True
- Prompt types: 20
- Tool types: 23
- Task routes: 33
- Bots with model routing: 1248 / 1248
- Bots with world model council: 1248 / 1248
- Bots with training/eval policy: 1248 / 1248

## Routing Rule

Provider model IDs, prices, rate limits, and availability change often. Treat every resource as a routing candidate and verify the current provider model ID before production use.

Prefer free-tier, local, cached, batch, and smallest-capable models for sandbox work. Escalate to paid or premium models only after cost review and owner approval.

## World Model Council

Use 100+ globally sourced model resources as a decision council for every bot while tracking strengths, weaknesses, cost, latency, safety, and task fit.

- Decision style: route_compare_debate_eval_then_select
- Actual resources: 104
- Provider count: 23

## Cost Control

- Default budget mode: free_or_low_cost_first
- Preferred sandbox family: google_gemini_flash_lite
- Secret name: GOOGLE_API_KEY

## Top Task Routes

- Architecture: openai_reasoning__quality
- Coding: deepseek_coder_reasoner__quality
- Debugging: deepseek_coder_reasoner__quality
- Repo Review: anthropic_claude__quality
- Market Research: perplexity_search__quality
- Competitor Analysis: perplexity_search__quality
- Sales Copy: ai21_language__quality
- Customer Support: ai21_language__quality
- Data Extraction: cohere_command__quality
- Dashboard Building: databricks_mosaic__quality
- Image Generation: adobe_firefly__quality
- Image Editing: adobe_firefly__quality

## Agent Types

- Planner Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Research Agent: prompts=retrieval_grounded, customer_discovery, offer_builder, critique, handoff_summary; tools=browser_research, vector_search, reranker, spreadsheet_builder, notification_sender
- Coding Agent: prompts=task_brief, tool_contract, code_review, test_generation, sandbox_runbook; tools=file_reader, code_editor, test_runner, api_client, approval_gate
- Debugging Agent: prompts=task_brief, tool_contract, code_review, test_generation, sandbox_runbook; tools=file_reader, code_editor, test_runner, api_client, approval_gate
- Tool Builder Agent: prompts=task_brief, tool_contract, code_review, test_generation, sandbox_runbook; tools=file_reader, code_editor, test_runner, api_client, approval_gate
- Workflow Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Sandbox Eval Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Creative Studio Agent: prompts=task_brief, visual_prompt, voice_consent, rubric_eval, handoff_summary; tools=image_generator, image_editor, video_generator, text_to_speech, approval_gate
- Voice Rights Agent: prompts=task_brief, visual_prompt, voice_consent, rubric_eval, handoff_summary; tools=image_generator, image_editor, video_generator, text_to_speech, approval_gate
- Business Owner Agent: prompts=retrieval_grounded, customer_discovery, offer_builder, critique, handoff_summary; tools=browser_research, vector_search, reranker, spreadsheet_builder, notification_sender
- Sales Agent: prompts=retrieval_grounded, customer_discovery, offer_builder, critique, handoff_summary; tools=browser_research, vector_search, reranker, spreadsheet_builder, notification_sender
- Data Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Security Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Legal Safety Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Memory Curator Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Model Router Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- World Model Council Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client
- Model Eval and Training Agent: prompts=task_brief, system_role, tool_contract, structured_output, few_shot; tools=file_reader, code_editor, test_runner, browser_research, api_client

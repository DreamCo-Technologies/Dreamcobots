"""
AI Companies Database — core intelligence for the DreamCo AI Level-Up Bot.

Stores 100+ significant AI companies, tools, and platforms across all major
categories, with fields required by the problem specification:
  - company_name
  - category
  - tools
  - pricing
  - region
  - api_available

Designed for scalability to 1000+ entries.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class AICompany:
    """Represents a single AI company or platform in the database."""

    company_name: str
    category: str
    tools: List[str]
    pricing: str
    region: str
    api_available: bool
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "category": self.category,
            "tools": self.tools,
            "pricing": self.pricing,
            "region": self.region,
            "api_available": self.api_available,
            "description": self.description,
        }


# ---------------------------------------------------------------------------
# Database seed data — 100+ companies across all categories
# ---------------------------------------------------------------------------

_COMPANIES: List[AICompany] = [
    # -----------------------------------------------------------------------
    # Core AI Model Companies
    # -----------------------------------------------------------------------
    AICompany(
        company_name="OpenAI",
        category="Core AI Models",
        tools=["ChatGPT", "DALL-E", "Sora", "GPT-4o", "Whisper", "Codex"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Leading AI research company behind GPT series and DALL-E.",
    ),
    AICompany(
        company_name="Anthropic",
        category="Core AI Models",
        tools=["Claude", "Claude Instant", "Claude 3 Opus", "Claude 3 Sonnet"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Safety-focused AI company building the Claude family of models.",
    ),
    AICompany(
        company_name="Google DeepMind",
        category="Core AI Models",
        tools=["Gemini", "Gemini Advanced", "AlphaCode", "AlphaFold", "Imagen"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Google's flagship AI research lab, creators of Gemini and AlphaFold.",
    ),
    AICompany(
        company_name="Microsoft",
        category="Core AI Models",
        tools=["Copilot", "Azure OpenAI Service", "Phi-3", "Bing AI"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Tech giant providing AI via Azure and integrated Copilot products.",
    ),
    AICompany(
        company_name="Meta Platforms",
        category="Core AI Models",
        tools=["Llama 3", "Llama 2", "Code Llama", "Segment Anything Model"],
        pricing="open-source",
        region="USA",
        api_available=True,
        description="Social media giant releasing open-source Llama models.",
    ),
    AICompany(
        company_name="Enterprise AI",
        category="Core AI Models",
        tools=["Enterprise AI", "enterprise AI", "Granite", "Enterprise Assistant"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Enterprise AI pioneer with Enterprise AI and enterprise AI platforms.",
    ),
    AICompany(
        company_name="Amazon",
        category="Core AI Models",
        tools=["Bedrock", "Titan", "CodeWhisperer", "Alexa AI", "SageMaker"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Cloud AI services via AWS Bedrock and SageMaker.",
    ),
    AICompany(
        company_name="DeepSeek",
        category="Core AI Models",
        tools=["DeepSeek-V2", "DeepSeek-Coder", "DeepSeek-R1"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="Chinese AI lab known for high-performance open-weight models.",
    ),
    AICompany(
        company_name="Mistral AI",
        category="Core AI Models",
        tools=["Mistral 7B", "Mixtral 8x7B", "Mistral Large", "Le Chat"],
        pricing="token-based",
        region="Europe",
        api_available=True,
        description="European AI lab building efficient open-weight language models.",
    ),
    AICompany(
        company_name="Cohere",
        category="Core AI Models",
        tools=["Command R+", "Embed", "Rerank", "Coral"],
        pricing="token-based",
        region="Canada",
        api_available=True,
        description="Enterprise NLP platform specialising in retrieval-augmented generation.",
    ),
    AICompany(
        company_name="xAI",
        category="Core AI Models",
        tools=["Grok", "Grok-2"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Elon Musk's AI company building the Grok assistant.",
    ),
    # -----------------------------------------------------------------------
    # AI Coding Platforms
    # -----------------------------------------------------------------------
    AICompany(
        company_name="GitHub",
        category="AI Coding Platforms",
        tools=["GitHub Copilot", "Copilot Chat", "Copilot Workspace"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Microsoft-owned platform offering AI-powered coding assistant.",
    ),
    AICompany(
        company_name="Replit",
        category="AI Coding Platforms",
        tools=["Replit AI", "Ghostwriter", "Replit Deployments"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Online coding environment with integrated AI assistant.",
    ),
    AICompany(
        company_name="Tabnine",
        category="AI Coding Platforms",
        tools=["Tabnine Autocomplete", "Tabnine Chat"],
        pricing="freemium",
        region="Israel",
        api_available=True,
        description="AI code completion tool for IDEs.",
    ),
    AICompany(
        company_name="Codeium",
        category="AI Coding Platforms",
        tools=["Windsurf", "Codeium Chat", "Codeium Autocomplete"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Free AI coding assistant with IDE plugins.",
    ),
    AICompany(
        company_name="Sourcegraph",
        category="AI Coding Platforms",
        tools=["Cody", "Code Search", "Batch Changes"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Code intelligence platform with AI-powered Cody assistant.",
    ),
    AICompany(
        company_name="Magic.dev",
        category="AI Coding Platforms",
        tools=["Magic LTM", "CTO AI"],
        pricing="subscription",
        region="USA",
        api_available=False,
        description="AI coding agent designed to act as a software engineer.",
    ),
    # -----------------------------------------------------------------------
    # AI Image Generation
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Midjourney",
        category="AI Image Generation",
        tools=["Midjourney v6", "Midjourney Niji"],
        pricing="subscription",
        region="USA",
        api_available=False,
        description="Leading AI image generation platform via Discord.",
    ),
    AICompany(
        company_name="Stability AI",
        category="AI Image Generation",
        tools=["Stable Diffusion", "Stable Diffusion XL", "Stable Video"],
        pricing="open-source",
        region="UK",
        api_available=True,
        description="Creator of the open-source Stable Diffusion image model.",
    ),
    AICompany(
        company_name="Freepik",
        category="AI Image Generation",
        tools=["Freepik AI Image Generator", "Pikaso"],
        pricing="freemium",
        region="Europe",
        api_available=True,
        description="Design platform with AI-powered image generation tools.",
    ),
    AICompany(
        company_name="Leonardo AI",
        category="AI Image Generation",
        tools=["Leonardo Diffusion XL", "Motion", "Universal Upscaler"],
        pricing="freemium",
        region="Australia",
        api_available=True,
        description="AI art platform focused on game assets and concept art.",
    ),
    AICompany(
        company_name="NightCafe Studio",
        category="AI Image Generation",
        tools=["NightCafe Creator", "Style Transfer", "Text to Image"],
        pricing="freemium",
        region="Australia",
        api_available=False,
        description="AI art generation platform with community features.",
    ),
    AICompany(
        company_name="Artbreeder",
        category="AI Image Generation",
        tools=["Artbreeder Collage", "Splicer", "Outpainter"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="Collaborative AI art platform for blending and creating images.",
    ),
    AICompany(
        company_name="Playground AI",
        category="AI Image Generation",
        tools=["Playground v2.5", "Canvas Editor"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI image generation platform for creative and commercial use.",
    ),
    # -----------------------------------------------------------------------
    # AI Video Generation
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Runway",
        category="AI Video Generation",
        tools=["Gen-3 Alpha", "Gen-2", "Runway Studio", "Motion Brush"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Pioneer in AI video generation and creative tools.",
    ),
    AICompany(
        company_name="Pika Labs",
        category="AI Video Generation",
        tools=["Pika 1.0", "Pika 2.0"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI video generation startup creating cinematic content.",
    ),
    AICompany(
        company_name="Synthesia",
        category="AI Video Generation",
        tools=["Synthesia Studio", "AI Avatars", "AI Voices"],
        pricing="subscription",
        region="UK",
        api_available=True,
        description="AI video platform for creating professional training videos.",
    ),
    AICompany(
        company_name="InVideo",
        category="AI Video Generation",
        tools=["InVideo AI", "Text to Video", "AI Script Generator"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI-powered video creation platform for marketers.",
    ),
    AICompany(
        company_name="Luma AI",
        category="AI Video Generation",
        tools=["Dream Machine", "Genie", "NeRF Capture"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="3D and video AI tools including the Dream Machine model.",
    ),
    AICompany(
        company_name="Wonder Dynamics",
        category="AI Video Generation",
        tools=["Wonder Studio"],
        pricing="subscription",
        region="USA",
        api_available=False,
        description="AI VFX tool that automates animation, lighting, and compositing.",
    ),
    # -----------------------------------------------------------------------
    # AI Voice & Audio
    # -----------------------------------------------------------------------
    AICompany(
        company_name="ElevenLabs",
        category="AI Voice & Audio",
        tools=["Voice Cloning", "Text to Speech", "Voice Design", "Dubbing"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Leading AI voice synthesis and cloning platform.",
    ),
    AICompany(
        company_name="PlayHT",
        category="AI Voice & Audio",
        tools=["PlayHT 2.0", "Voice Cloning", "Text to Speech API"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI voice generation platform with realistic speech synthesis.",
    ),
    AICompany(
        company_name="Resemble AI",
        category="AI Voice & Audio",
        tools=["Voice Builder", "Neural TTS", "Speech to Speech"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="AI voice cloning and generation for media production.",
    ),
    AICompany(
        company_name="Descript",
        category="AI Voice & Audio",
        tools=["Overdub", "Studio Sound", "AI Script Writer", "Transcription"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="All-in-one audio/video editor with AI-powered voice tools.",
    ),
    AICompany(
        company_name="Speechify",
        category="AI Voice & Audio",
        tools=["Text to Speech", "Voice Over Studio", "AI Reader"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI text-to-speech and audio reading platform.",
    ),
    # -----------------------------------------------------------------------
    # AI Music
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Suno AI",
        category="AI Music",
        tools=["Suno v3", "Chirp", "AI Song Generator"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI music generation platform creating full songs from prompts.",
    ),
    AICompany(
        company_name="Udio",
        category="AI Music",
        tools=["Udio Music Generator", "Remix"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI music generation platform for original compositions.",
    ),
    AICompany(
        company_name="Soundful",
        category="AI Music",
        tools=["Royalty-Free Music Generator", "Template Composer"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI music platform generating royalty-free background tracks.",
    ),
    AICompany(
        company_name="Boomy",
        category="AI Music",
        tools=["Song Creator", "AI Mastering", "Distribution"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI music creation platform for instant song generation.",
    ),
    # -----------------------------------------------------------------------
    # AI Productivity Tools
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Grammarly",
        category="AI Productivity Tools",
        tools=["Grammarly Editor", "GrammarlyGO", "Grammarly Business"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI writing assistant for grammar, clarity, and tone.",
    ),
    AICompany(
        company_name="Jasper AI",
        category="AI Productivity Tools",
        tools=["Jasper Chat", "Jasper Art", "Brand Voice", "Campaigns"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="AI content creation platform for marketing teams.",
    ),
    AICompany(
        company_name="Notion",
        category="AI Productivity Tools",
        tools=["Notion AI", "Notion Databases", "Notion Calendar"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="All-in-one workspace with embedded AI writing assistance.",
    ),
    AICompany(
        company_name="Otter.ai",
        category="AI Productivity Tools",
        tools=["AI Meeting Transcription", "OtterPilot", "AI Chat"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI meeting transcription and note-taking platform.",
    ),
    AICompany(
        company_name="ClickUp",
        category="AI Productivity Tools",
        tools=["ClickUp AI", "Task Automation", "Docs AI"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Project management platform with built-in AI assistance.",
    ),
    # -----------------------------------------------------------------------
    # AI Agents & Automation
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Zapier",
        category="AI Agents & Automation",
        tools=["Zaps", "Zapier AI", "Tables", "Interfaces", "Chatbots"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Workflow automation platform connecting 6000+ apps.",
    ),
    AICompany(
        company_name="UiPath",
        category="AI Agents & Automation",
        tools=["UiPath Studio", "Autopilot", "Document Understanding", "Process Mining"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Enterprise RPA platform with AI-powered automation.",
    ),
    AICompany(
        company_name="Automation Anywhere",
        category="AI Agents & Automation",
        tools=["AARI", "IQ Bot", "Process Discovery", "RPA"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Intelligent automation platform for enterprise workflows.",
    ),
    AICompany(
        company_name="Conversica",
        category="AI Agents & Automation",
        tools=["AI Revenue Digital Assistants", "Lead Engagement"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="AI-powered revenue digital assistants for sales automation.",
    ),
    # -----------------------------------------------------------------------
    # AI Infrastructure Platforms
    # -----------------------------------------------------------------------
    AICompany(
        company_name="NVIDIA",
        category="AI Infrastructure Platforms",
        tools=["CUDA", "NIM", "DGX", "TensorRT", "NeMo", "DIGITS"],
        pricing="hardware+software",
        region="USA",
        api_available=True,
        description="GPU hardware and AI software infrastructure provider.",
    ),
    AICompany(
        company_name="Hugging Face",
        category="AI Infrastructure Platforms",
        tools=["Transformers", "Diffusers", "Hub", "Spaces", "Inference API"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Open-source ML platform and model hosting hub.",
    ),
    AICompany(
        company_name="Together AI",
        category="AI Infrastructure Platforms",
        tools=["Together Inference", "Fine-tuning API", "Together Cloud"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Cloud platform for running and fine-tuning open-source models.",
    ),
    AICompany(
        company_name="Scale AI",
        category="AI Infrastructure Platforms",
        tools=["Data Engine", "RLHF", "Evaluation", "Donovan"],
        pricing="enterprise",
        region="USA",
        api_available=True,
        description="AI data platform for training data labeling and evaluation.",
    ),
    AICompany(
        company_name="Replicate",
        category="AI Infrastructure Platforms",
        tools=["Model Deployment", "Fine-tuning", "Predictions API"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Cloud platform for running open-source AI models via API.",
    ),
    # -----------------------------------------------------------------------
    # Major Chinese AI Companies
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Baidu",
        category="Major Chinese AI Companies",
        tools=["ERNIE Bot", "ERNIE 4.0", "Wenxin", "PaddlePaddle"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="China's leading search engine and AI research company.",
    ),
    AICompany(
        company_name="Alibaba",
        category="Major Chinese AI Companies",
        tools=["Qwen", "Tongyi Qianwen", "PAI", "ModelScope"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="Chinese e-commerce giant with AI research via DAMO Academy.",
    ),
    AICompany(
        company_name="Tencent",
        category="Major Chinese AI Companies",
        tools=["Hunyuan", "Tencent Cloud AI", "WeChat AI"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="Chinese tech conglomerate with Hunyuan large language model.",
    ),
    AICompany(
        company_name="SenseTime",
        category="Major Chinese AI Companies",
        tools=["SenseNova", "SenseCore", "SenseMARS", "SenseCare"],
        pricing="enterprise",
        region="China",
        api_available=True,
        description="Chinese AI company specialising in computer vision.",
    ),
    AICompany(
        company_name="iFlytek",
        category="Major Chinese AI Companies",
        tools=["Spark Cognitive Model", "AI Translation", "Voice Recognition"],
        pricing="subscription",
        region="China",
        api_available=True,
        description="Chinese AI company known for speech recognition technology.",
    ),
    # -----------------------------------------------------------------------
    # European AI Leaders
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Aleph Alpha",
        category="European AI Leaders",
        tools=["Luminous", "Pharia-1", "Aleph Alpha API"],
        pricing="token-based",
        region="Europe",
        api_available=True,
        description="German AI company building sovereign large language models.",
    ),
    # -----------------------------------------------------------------------
    # AI for Science & Healthcare
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Insilico Medicine",
        category="AI for Science & Healthcare",
        tools=["Chemistry42", "PandaOmics", "InClinico"],
        pricing="enterprise",
        region="Hong Kong",
        api_available=False,
        description="AI-driven drug discovery and development company.",
    ),
    AICompany(
        company_name="Deep Genomics",
        category="AI for Science & Healthcare",
        tools=["BigRNA", "AI Drug Discovery Platform"],
        pricing="enterprise",
        region="Canada",
        api_available=False,
        description="AI platform for genetic medicine and RNA therapy design.",
    ),
    AICompany(
        company_name="Tempus",
        category="AI for Science & Healthcare",
        tools=["Lens", "Next", "Time Trial", "Radiology AI"],
        pricing="enterprise",
        region="USA",
        api_available=True,
        description="AI technology company advancing precision medicine.",
    ),
    # -----------------------------------------------------------------------
    # Additional notable companies (reaching 100+ total)
    # -----------------------------------------------------------------------
    AICompany(
        company_name="Perplexity AI",
        category="Core AI Models",
        tools=["Perplexity Search", "Perplexity Pro", "Sonar API"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI-powered conversational search engine.",
    ),
    AICompany(
        company_name="Adobe",
        category="AI Image Generation",
        tools=["Firefly", "Generative Fill", "Text to Image", "Express AI"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Creative software company with AI-powered Firefly models.",
    ),
    AICompany(
        company_name="Canva",
        category="AI Productivity Tools",
        tools=["Magic Studio", "Magic Write", "Text to Image", "Presentations AI"],
        pricing="freemium",
        region="Australia",
        api_available=True,
        description="Design platform with extensive AI generation features.",
    ),
    AICompany(
        company_name="Make (Integromat)",
        category="AI Agents & Automation",
        tools=["Visual Automation Builder", "AI Scenarios", "HTTP Module"],
        pricing="freemium",
        region="Europe",
        api_available=True,
        description="Visual automation platform for no-code workflow building.",
    ),
    AICompany(
        company_name="Coze",
        category="AI Agents & Automation",
        tools=["Bot Builder", "Plugin Store", "Knowledge Base", "Workflows"],
        pricing="freemium",
        region="China",
        api_available=True,
        description="ByteDance's AI bot development platform.",
    ),
    AICompany(
        company_name="Character AI",
        category="Core AI Models",
        tools=["Character Chat", "Character Creation", "Group Chats"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="Platform for creating and conversing with AI characters.",
    ),
    AICompany(
        company_name="Pi (Inflection AI)",
        category="Core AI Models",
        tools=["Pi Personal AI", "Inflection-2.5"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="Personal AI assistant from Inflection AI.",
    ),
    AICompany(
        company_name="Ideogram",
        category="AI Image Generation",
        tools=["Ideogram 2.0", "Text in Image", "Canvas"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI image generation with superior text rendering.",
    ),
    AICompany(
        company_name="Kling AI",
        category="AI Video Generation",
        tools=["Kling 1.5", "Kling Video", "Image to Video"],
        pricing="freemium",
        region="China",
        api_available=True,
        description="Kuaishou's AI video generation platform.",
    ),
    AICompany(
        company_name="HeyGen",
        category="AI Video Generation",
        tools=["AI Avatars", "Video Translation", "Interactive Avatar"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="AI video generation platform featuring realistic avatars.",
    ),
    AICompany(
        company_name="Murf AI",
        category="AI Voice & Audio",
        tools=["AI Voice Generator", "Voice Changer", "Voice Cloning"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI voiceover studio for professionals.",
    ),
    AICompany(
        company_name="Suno",
        category="AI Music",
        tools=["Song Generation", "Lyrics Generation", "Remix"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI music generation creating full songs from text prompts.",
    ),
    AICompany(
        company_name="Copy.ai",
        category="AI Productivity Tools",
        tools=["Workflows", "Brand Voice", "AI Chat", "Infobase"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI marketing copy and content generation platform.",
    ),
    AICompany(
        company_name="Writesonic",
        category="AI Productivity Tools",
        tools=["Chatsonic", "AI Article Writer", "Botsonic", "Audiosonic"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI writing and chatbot creation platform.",
    ),
    AICompany(
        company_name="Runway ML",
        category="AI Coding Platforms",
        tools=["ML Tools", "Green Screen AI", "Frame Interpolation"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Creative ML tools for artists and developers.",
    ),
    AICompany(
        company_name="Weights & Biases",
        category="AI Infrastructure Platforms",
        tools=["W&B Runs", "Weave", "W&B Artifacts", "Sweeps"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="MLOps platform for experiment tracking and model management.",
    ),
    AICompany(
        company_name="Modal",
        category="AI Infrastructure Platforms",
        tools=["Serverless GPU", "Deployments", "Sandboxes", "Cron Jobs"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Cloud infrastructure for running ML workloads serverlessly.",
    ),
    AICompany(
        company_name="Vertex AI",
        category="AI Infrastructure Platforms",
        tools=["Model Garden", "Gemini API", "AutoML", "Pipelines"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="Google Cloud's unified ML platform.",
    ),
    AICompany(
        company_name="LeMind (Moonshot AI)",
        category="Major Chinese AI Companies",
        tools=["Kimi Chat", "Kimi API"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="Chinese AI startup building long-context language models.",
    ),
    AICompany(
        company_name="Zhipu AI",
        category="Major Chinese AI Companies",
        tools=["GLM-4", "ChatGLM", "CogVideo", "CogView"],
        pricing="token-based",
        region="China",
        api_available=True,
        description="Chinese AI company building the GLM family of models.",
    ),
    AICompany(
        company_name="01.AI",
        category="Major Chinese AI Companies",
        tools=["Yi-34B", "Yi-VL", "Yi-6B"],
        pricing="open-source",
        region="China",
        api_available=True,
        description="Kai-Fu Lee's AI company releasing open-source Yi models.",
    ),
    AICompany(
        company_name="Poolside AI",
        category="AI Coding Platforms",
        tools=["Poolside Assistant", "Malibu"],
        pricing="subscription",
        region="USA",
        api_available=False,
        description="AI coding assistant trained on software engineering tasks.",
    ),
    AICompany(
        company_name="Cursor",
        category="AI Coding Platforms",
        tools=["Cursor IDE", "Tab Autocomplete", "Composer"],
        pricing="freemium",
        region="USA",
        api_available=False,
        description="AI-first code editor forked from VS Code.",
    ),
    AICompany(
        company_name="Airtable",
        category="AI Productivity Tools",
        tools=["Airtable AI", "Automations", "Interfaces", "Views"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Low-code platform with AI-powered data management.",
    ),
    AICompany(
        company_name="Elicit",
        category="AI for Science & Healthcare",
        tools=["Literature Review", "Paper Summarizer", "Data Extraction"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="AI research assistant for scientific literature review.",
    ),
    AICompany(
        company_name="Recursion Pharmaceuticals",
        category="AI for Science & Healthcare",
        tools=["Recursion OS", "RxRx Datasets", "Drug Discovery Platform"],
        pricing="enterprise",
        region="USA",
        api_available=False,
        description="Biopharmaceutical company using AI to decode biology.",
    ),
    AICompany(
        company_name="Twelve Labs",
        category="AI Video Generation",
        tools=["Marengo", "Pegasus", "Video Understanding API"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="AI video understanding and search platform.",
    ),
    AICompany(
        company_name="AssemblyAI",
        category="AI Voice & Audio",
        tools=["Transcription API", "Universal-2", "LeMUR", "Audio Intelligence"],
        pricing="token-based",
        region="USA",
        api_available=True,
        description="AI platform for speech recognition and audio intelligence.",
    ),
    AICompany(
        company_name="Speechmatics",
        category="AI Voice & Audio",
        tools=["Automatic Speech Recognition", "Real-Time API", "Transcription"],
        pricing="token-based",
        region="UK",
        api_available=True,
        description="UK-based AI speech recognition platform with high accuracy.",
    ),
    # -----------------------------------------------------------------------
    # Additional notable companies (reaching 100+ total)
    # -----------------------------------------------------------------------
    AICompany(
        company_name="LangChain",
        category="AI Agents & Automation",
        tools=["LangChain Framework", "LangSmith", "LangGraph"],
        pricing="open-source",
        region="USA",
        api_available=True,
        description="Open-source framework for building LLM-powered applications.",
    ),
    AICompany(
        company_name="Pinecone",
        category="AI Infrastructure Platforms",
        tools=["Vector Database", "Pinecone Index", "Serverless"],
        pricing="freemium",
        region="USA",
        api_available=True,
        description="Managed vector database for AI-powered search and retrieval.",
    ),
    AICompany(
        company_name="Weaviate",
        category="AI Infrastructure Platforms",
        tools=["Vector Store", "Weaviate Cloud", "Generative Search"],
        pricing="open-source",
        region="Europe",
        api_available=True,
        description="Open-source vector database for AI applications.",
    ),
    AICompany(
        company_name="Silo AI",
        category="European AI Leaders",
        tools=["SiloGen", "Enterprise AI Models", "Private LLMs"],
        pricing="enterprise",
        region="Europe",
        api_available=False,
        description="Finland-based AI company building customised enterprise AI.",
    ),
    AICompany(
        company_name="Helsing",
        category="European AI Leaders",
        tools=["HX-1", "Sensor Fusion", "Defence AI"],
        pricing="enterprise",
        region="Europe",
        api_available=False,
        description="European AI defence company applying AI to security.",
    ),
    AICompany(
        company_name="Writer",
        category="AI Productivity Tools",
        tools=["Writer Platform", "Palmyra LLM", "CoWrite"],
        pricing="subscription",
        region="USA",
        api_available=True,
        description="Enterprise AI writing platform with custom LLMs.",
    ),
    AICompany(
        company_name="Glean",
        category="AI Productivity Tools",
        tools=["Work AI Platform", "Glean Chat", "Glean Search"],
        pricing="enterprise",
        region="USA",
        api_available=True,
        description="Enterprise AI search and knowledge discovery platform.",
    ),
    AICompany(
        company_name="Corti AI",
        category="AI for Science & Healthcare",
        tools=["Corti Assistant", "Ambient Documentation", "Clinical Decision Support"],
        pricing="enterprise",
        region="Europe",
        api_available=False,
        description="AI platform for real-time clinical decision support.",
    ),
    AICompany(
        company_name="Wayve",
        category="AI for Science & Healthcare",
        tools=["LINGO-1", "Embodied Intelligence", "AV Software"],
        pricing="enterprise",
        region="UK",
        api_available=False,
        description="AI company building foundation models for autonomous driving.",
    ),
    AICompany(
        company_name="n8n",
        category="AI Agents & Automation",
        tools=["n8n Workflow Automation", "AI Agent Nodes", "Self-Hosted"],
        pricing="open-source",
        region="Europe",
        api_available=True,
        description="Open-source workflow automation with AI agent capabilities.",
    ),
]


class AICompanyDatabase:
    """Database of AI companies and platforms.

    Provides search, filter, and retrieval methods over the curated list
    of 100+ AI companies. Designed to scale to 1000+ entries.

    Parameters
    ----------
    extra_companies : list[AICompany] | None
        Additional companies to merge into the default dataset.
    """

    def __init__(self, extra_companies: Optional[List[AICompany]] = None) -> None:
        self._companies: List[AICompany] = list(_COMPANIES)
        if extra_companies:
            self._companies.extend(extra_companies)

    # ------------------------------------------------------------------
    # Core retrieval
    # ------------------------------------------------------------------

    def get_all(self) -> List[AICompany]:
        """Return all companies in the database."""
        return list(self._companies)

    def count(self) -> int:
        """Return the total number of companies in the database."""
        return len(self._companies)

    def get_company(self, name: str) -> Optional[AICompany]:
        """Return a company by exact or case-insensitive name match."""
        name_lower = name.lower()
        for company in self._companies:
            if company.company_name.lower() == name_lower:
                return company
        return None

    def get_tool(self, tool_name: str) -> Optional[AICompany]:
        """Return the first company that offers the named tool.

        Supports case-insensitive partial matching against tool names.
        """
        tool_lower = tool_name.lower()
        for company in self._companies:
            for tool in company.tools:
                if tool_lower in tool.lower():
                    return company
        return None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def get_by_category(self, category: str) -> List[AICompany]:
        """Return all companies in the given category (case-insensitive)."""
        cat_lower = category.lower()
        return [c for c in self._companies if c.category.lower() == cat_lower]

    def get_by_region(self, region: str) -> List[AICompany]:
        """Return all companies from the given region (case-insensitive)."""
        region_lower = region.lower()
        return [c for c in self._companies if c.region.lower() == region_lower]

    def get_with_api(self) -> List[AICompany]:
        """Return all companies that offer a public API."""
        return [c for c in self._companies if c.api_available]

    def get_by_pricing(self, pricing: str) -> List[AICompany]:
        """Return all companies with the specified pricing model."""
        pricing_lower = pricing.lower()
        return [c for c in self._companies if c.pricing.lower() == pricing_lower]

    def list_categories(self) -> List[str]:
        """Return a sorted, deduplicated list of all categories."""
        return sorted({c.category for c in self._companies})

    def list_regions(self) -> List[str]:
        """Return a sorted, deduplicated list of all regions."""
        return sorted({c.region for c in self._companies})

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_company(self, company: AICompany) -> None:
        """Add a new company to the database."""
        self._companies.append(company)

    def to_dict_list(self) -> List[dict]:
        """Serialise the full database to a list of dicts."""
        return [c.to_dict() for c in self._companies]

# DataForge AI API Guide

This guide covers all 100 API connectors available in the DataForge AI system.

## Using the APIManager

```python
from bots.dataforge.apis.api_manager import APIManager

manager = APIManager()
# List all available connectors
print(manager.list_connectors())  # Returns 100 connector names

# Get a specific connector
openai = manager.get_connector("openai")
result = openai.generate_text("Hello, world!")
```

## API Categories

### AI & Machine Learning (15 connectors)
- **openai** - OpenAI GPT models (gpt-4o, gpt-3.5-turbo)
- **huggingface** - HuggingFace Inference API
- **google_gemini** - Google Gemini generative AI
- **cohere** - Cohere generation and embeddings
- **mistral** - Mistral AI chat models
- **together_ai** - Together AI open source models
- **replicate** - Replicate model deployment
- **deepai** - DeepAI text and image APIs
- **stability_ai** - Stable Diffusion image generation
- **clarifai** - Clarifai visual AI
- **eden_ai** - Eden AI multi-provider hub
- **nlp_cloud** - NLP Cloud hosted models
- **monkeylearn** - MonkeyLearn text classification
- **wit_ai** - Wit.ai NLU (Meta)
- **dialogflow** - Google Dialogflow

### Speech & Voice (10 connectors)
- **mozilla_common_voice** - Open voice dataset
- **assemblyai** - AssemblyAI transcription
- **speechly** - Real-time ASR
- **deepgram** - Deepgram nova-2 model
- **rev_ai** - Rev.ai professional transcription
- **vosk** - Offline Vosk ASR
- **picovoice** - Wake word detection
- **speechbrain** - SpeechBrain toolkit
- **whisper** - OpenAI Whisper
- **elevenlabs** - ElevenLabs TTS

### Computer Vision (10 connectors)
- **facepp** - Face++ facial recognition
- **aws_rekognition** - AWS Rekognition
- **google_vision** - Google Cloud Vision
- **azure_face** - Azure Face API
- **deepface** - DeepFace library
- **opencv** - OpenCV Haar cascade
- **roboflow** - Roboflow inference
- **imagga** - Imagga tagging
- **clarifai_vision** - Clarifai general detection
- **tensorflow_vision** - TensorFlow classification

### Datasets & Research (15 connectors)
- **kaggle** - Kaggle datasets
- **huggingface_datasets** - HuggingFace Datasets
- **nasa** - NASA Open APIs (APOD, images)
- **world_bank** - World Bank indicators
- **datagov** - Data.gov catalog
- **un_data** - UN Data statistics
- **noaa_climate** - NOAA climate data
- **pubmed** - PubMed biomedical articles
- **arxiv** - ArXiv preprints
- **semantic_scholar** - Semantic Scholar
- **crossref** - CrossRef DOI metadata
- **core** - CORE open access
- **openalex** - OpenAlex scholarly graph
- **eurostat** - Eurostat EU statistics

### Finance & Crypto (10 connectors)
- **coingecko** - CoinGecko prices
- **alpha_vantage** - Stock and forex
- **finnhub** - Financial data
- **fixer** - Exchange rates
- **open_exchange_rates** - Currency data
- **coincap** - CoinCap crypto
- **polygon** - Polygon.io stocks
- **yahoo_finance** - Yahoo Finance
- **quandl** - Nasdaq/Quandl datasets
- **cryptocompare** - Crypto data

### Weather & Climate (7 connectors)
- **openweathermap** - Current and forecast weather
- **open_meteo** - Free weather API (no key)
- **weatherapi** - WeatherAPI.com
- **visual_crossing** - Historical weather
- **storm_glass** - Marine weather
- **airvisual** - Air quality data
- **climacell** - Tomorrow.io weather intelligence

### News & Media (7 connectors)
- **newsapi** - Global news aggregator
- **gnews** - GNews search
- **currents** - Currents API
- **guardian** - The Guardian
- **nytimes** - New York Times
- **mediastack** - MediaStack live news
- **bing_news** - Bing News Search

### E-Commerce (6 connectors)
- **open_food_facts** - Nutrition data (no key)
- **best_buy** - Best Buy products
- **ebay** - eBay Browse API
- **etsy** - Etsy marketplace
- **barcode_lookup** - Barcode Lookup
- **upc_itemdb** - UPC ItemDB

### Social & Communication (10 connectors)
- **reddit** - Reddit public API
- **twitter** - Twitter/X API v2
- **discord** - Discord Bot API
- **telegram** - Telegram Bot
- **twilio** - SMS and voice calls
- **sendgrid** - Transactional email
- **twitch** - Twitch streams
- **spotify** - Spotify catalog
- **youtube** - YouTube Data API

### Location & Maps (6 connectors)
- **openstreetmap** - Nominatim geocoding (no key)
- **google_maps** - Google Maps
- **mapbox** - Mapbox geocoding
- **opencage** - OpenCage geocoding
- **ip_api** - IP geolocation (no key)
- **what3words** - What3Words

### Utilities & Misc (5 connectors)
- **qr_code** - QR code generation (no key)
- **bitly** - URL shortener
- **mailchimp** - Email marketing
- **stripe** - Payments processing
- **paypal** - PayPal orders
- **github** - GitHub REST API

## Environment Variables

Set these environment variables for the APIs you want to use:

```bash
# AI & ML
OPENAI_API_KEY=...
HUGGINGFACE_TOKEN=...
GOOGLE_GEMINI_API_KEY=...
COHERE_API_KEY=...
MISTRAL_API_KEY=...

# Speech
ASSEMBLYAI_API_KEY=...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

# Vision
GOOGLE_VISION_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Finance
ALPHA_VANTAGE_API_KEY=...
STRIPE_SECRET_KEY=...

# See api_registry.py for complete list
```

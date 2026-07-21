"""API Manager for DataForge AI - lazy-loads all 100 API connectors."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import importlib
import logging

logger = logging.getLogger(__name__)

CONNECTOR_MODULE_MAP = {
    "openai": ("bots.dataforge.apis.connectors.openai_connector", "OpenAIConnector"),
    "huggingface": ("bots.dataforge.apis.connectors.huggingface_connector", "HuggingFaceConnector"),
    "google_gemini": ("bots.dataforge.apis.connectors.google_gemini_connector", "GoogleGeminiConnector"),
    "cohere": ("bots.dataforge.apis.connectors.cohere_connector", "CohereConnector"),
    "mistral": ("bots.dataforge.apis.connectors.mistral_connector", "MistralConnector"),
    "together_ai": ("bots.dataforge.apis.connectors.together_ai_connector", "TogetherAIConnector"),
    "replicate": ("bots.dataforge.apis.connectors.replicate_connector", "ReplicateConnector"),
    "deepai": ("bots.dataforge.apis.connectors.deepai_connector", "DeepAIConnector"),
    "stability_ai": ("bots.dataforge.apis.connectors.stability_ai_connector", "StabilityAIConnector"),
    "clarifai": ("bots.dataforge.apis.connectors.clarifai_connector", "ClarifaiConnector"),
    "eden_ai": ("bots.dataforge.apis.connectors.eden_ai_connector", "EdenAIConnector"),
    "nlp_cloud": ("bots.dataforge.apis.connectors.nlp_cloud_connector", "NLPCloudConnector"),
    "monkeylearn": ("bots.dataforge.apis.connectors.monkeylearn_connector", "MonkeyLearnConnector"),
    "wit_ai": ("bots.dataforge.apis.connectors.wit_ai_connector", "WitAIConnector"),
    "dialogflow": ("bots.dataforge.apis.connectors.dialogflow_connector", "DialogflowConnector"),
    "mozilla_common_voice": ("bots.dataforge.apis.connectors.mozilla_common_voice_connector", "MozillaCommonVoiceConnector"),
    "assemblyai": ("bots.dataforge.apis.connectors.assemblyai_connector", "AssemblyAIConnector"),
    "speechly": ("bots.dataforge.apis.connectors.speechly_connector", "SpeechlyConnector"),
    "deepgram": ("bots.dataforge.apis.connectors.deepgram_connector", "DeepgramConnector"),
    "rev_ai": ("bots.dataforge.apis.connectors.rev_ai_connector", "RevAIConnector"),
    "vosk": ("bots.dataforge.apis.connectors.vosk_connector", "VoskConnector"),
    "picovoice": ("bots.dataforge.apis.connectors.picovoice_connector", "PicovoiceConnector"),
    "speechbrain": ("bots.dataforge.apis.connectors.speechbrain_connector", "SpeechBrainConnector"),
    "whisper": ("bots.dataforge.apis.connectors.whisper_connector", "WhisperConnector"),
    "elevenlabs": ("bots.dataforge.apis.connectors.elevenlabs_connector", "ElevenLabsConnector"),
    "facepp": ("bots.dataforge.apis.connectors.facepp_connector", "FacePPConnector"),
    "aws_rekognition": ("bots.dataforge.apis.connectors.aws_rekognition_connector", "AWSRekognitionConnector"),
    "google_vision": ("bots.dataforge.apis.connectors.google_vision_connector", "GoogleVisionConnector"),
    "azure_face": ("bots.dataforge.apis.connectors.azure_face_connector", "AzureFaceConnector"),
    "deepface": ("bots.dataforge.apis.connectors.deepface_connector", "DeepFaceConnector"),
    "opencv": ("bots.dataforge.apis.connectors.opencv_connector", "OpenCVConnector"),
    "roboflow": ("bots.dataforge.apis.connectors.roboflow_connector", "RoboflowConnector"),
    "imagga": ("bots.dataforge.apis.connectors.imagga_connector", "ImaggaConnector"),
    "clarifai_vision": ("bots.dataforge.apis.connectors.clarifai_vision_connector", "ClarifaiVisionConnector"),
    "tensorflow_vision": ("bots.dataforge.apis.connectors.tensorflow_vision_connector", "TensorFlowVisionConnector"),
    "kaggle": ("bots.dataforge.apis.connectors.kaggle_connector", "KaggleConnector"),
    "huggingface_datasets": ("bots.dataforge.apis.connectors.huggingface_datasets_connector", "HuggingFaceDatasetsConnector"),
    "nasa": ("bots.dataforge.apis.connectors.nasa_connector", "NASAConnector"),
    "world_bank": ("bots.dataforge.apis.connectors.world_bank_connector", "WorldBankConnector"),
    "datagov": ("bots.dataforge.apis.connectors.datagov_connector", "DataGovConnector"),
    "openstreetmap": ("bots.dataforge.apis.connectors.openstreetmap_connector", "OpenStreetMapConnector"),
    "un_data": ("bots.dataforge.apis.connectors.un_data_connector", "UNDataConnector"),
    "noaa_climate": ("bots.dataforge.apis.connectors.noaa_climate_connector", "NOAAClimateConnector"),
    "pubmed": ("bots.dataforge.apis.connectors.pubmed_connector", "PubMedConnector"),
    "arxiv": ("bots.dataforge.apis.connectors.arxiv_connector", "ArXivConnector"),
    "semantic_scholar": ("bots.dataforge.apis.connectors.semantic_scholar_connector", "SemanticScholarConnector"),
    "crossref": ("bots.dataforge.apis.connectors.crossref_connector", "CrossRefConnector"),
    "core": ("bots.dataforge.apis.connectors.core_connector", "COREConnector"),
    "openalex": ("bots.dataforge.apis.connectors.openalex_connector", "OpenAlexConnector"),
    "eurostat": ("bots.dataforge.apis.connectors.eurostat_connector", "EurostatConnector"),
    "coingecko": ("bots.dataforge.apis.connectors.coingecko_connector", "CoinGeckoConnector"),
    "alpha_vantage": ("bots.dataforge.apis.connectors.alpha_vantage_connector", "AlphaVantageConnector"),
    "finnhub": ("bots.dataforge.apis.connectors.finnhub_connector", "FinnhubConnector"),
    "fixer": ("bots.dataforge.apis.connectors.fixer_connector", "FixerConnector"),
    "open_exchange_rates": ("bots.dataforge.apis.connectors.open_exchange_rates_connector", "OpenExchangeRatesConnector"),
    "coincap": ("bots.dataforge.apis.connectors.coincap_connector", "CoinCapConnector"),
    "polygon": ("bots.dataforge.apis.connectors.polygon_connector", "PolygonConnector"),
    "yahoo_finance": ("bots.dataforge.apis.connectors.yahoo_finance_connector", "YahooFinanceConnector"),
    "quandl": ("bots.dataforge.apis.connectors.quandl_connector", "QuandlConnector"),
    "cryptocompare": ("bots.dataforge.apis.connectors.cryptocompare_connector", "CryptoCompareConnector"),
    "openweathermap": ("bots.dataforge.apis.connectors.openweathermap_connector", "OpenWeatherMapConnector"),
    "open_meteo": ("bots.dataforge.apis.connectors.open_meteo_connector", "OpenMeteoConnector"),
    "weatherapi": ("bots.dataforge.apis.connectors.weatherapi_connector", "WeatherAPIConnector"),
    "visual_crossing": ("bots.dataforge.apis.connectors.visual_crossing_connector", "VisualCrossingConnector"),
    "storm_glass": ("bots.dataforge.apis.connectors.storm_glass_connector", "StormGlassConnector"),
    "airvisual": ("bots.dataforge.apis.connectors.airvisual_connector", "AirVisualConnector"),
    "climacell": ("bots.dataforge.apis.connectors.climacell_connector", "ClimacellConnector"),
    "newsapi": ("bots.dataforge.apis.connectors.newsapi_connector", "NewsAPIConnector"),
    "gnews": ("bots.dataforge.apis.connectors.gnews_connector", "GNewsConnector"),
    "currents": ("bots.dataforge.apis.connectors.currents_connector", "CurrentsConnector"),
    "guardian": ("bots.dataforge.apis.connectors.guardian_connector", "GuardianConnector"),
    "nytimes": ("bots.dataforge.apis.connectors.nytimes_connector", "NYTimesConnector"),
    "mediastack": ("bots.dataforge.apis.connectors.mediastack_connector", "MediaStackConnector"),
    "bing_news": ("bots.dataforge.apis.connectors.bing_news_connector", "BingNewsConnector"),
    "open_food_facts": ("bots.dataforge.apis.connectors.open_food_facts_connector", "OpenFoodFactsConnector"),
    "best_buy": ("bots.dataforge.apis.connectors.best_buy_connector", "BestBuyConnector"),
    "ebay": ("bots.dataforge.apis.connectors.ebay_connector", "EbayConnector"),
    "etsy": ("bots.dataforge.apis.connectors.etsy_connector", "EtsyConnector"),
    "barcode_lookup": ("bots.dataforge.apis.connectors.barcode_lookup_connector", "BarcodeLookupConnector"),
    "upc_itemdb": ("bots.dataforge.apis.connectors.upc_itemdb_connector", "UPCItemDBConnector"),
    "reddit": ("bots.dataforge.apis.connectors.reddit_connector", "RedditConnector"),
    "twitter": ("bots.dataforge.apis.connectors.twitter_connector", "TwitterConnector"),
    "discord": ("bots.dataforge.apis.connectors.discord_connector", "DiscordConnector"),
    "telegram": ("bots.dataforge.apis.connectors.telegram_connector", "TelegramConnector"),
    "twilio": ("bots.dataforge.apis.connectors.twilio_connector", "TwilioConnector"),
    "sendgrid": ("bots.dataforge.apis.connectors.sendgrid_connector", "SendGridConnector"),
    "google_maps": ("bots.dataforge.apis.connectors.google_maps_connector", "GoogleMapsConnector"),
    "mapbox": ("bots.dataforge.apis.connectors.mapbox_connector", "MapboxConnector"),
    "opencage": ("bots.dataforge.apis.connectors.opencage_connector", "OpenCageConnector"),
    "ip_api": ("bots.dataforge.apis.connectors.ip_api_connector", "IPAPIConnector"),
    "what3words": ("bots.dataforge.apis.connectors.what3words_connector", "What3WordsConnector"),
    "qr_code": ("bots.dataforge.apis.connectors.qr_code_connector", "QRCodeConnector"),
    "bitly": ("bots.dataforge.apis.connectors.bitly_connector", "BitlyConnector"),
    "mailchimp": ("bots.dataforge.apis.connectors.mailchimp_connector", "MailchimpConnector"),
    "stripe": ("bots.dataforge.apis.connectors.stripe_connector", "StripeConnector"),
    "paypal": ("bots.dataforge.apis.connectors.paypal_connector", "PayPalConnector"),
    "twitch": ("bots.dataforge.apis.connectors.twitch_connector", "TwitchConnector"),
    "spotify": ("bots.dataforge.apis.connectors.spotify_connector", "SpotifyConnector"),
    "youtube": ("bots.dataforge.apis.connectors.youtube_connector", "YouTubeConnector"),
    "github": ("bots.dataforge.apis.connectors.github_connector", "GitHubConnector"),
}


class APIManager:
    """Lazy-loading manager for all 100 DataForge AI API connectors."""

    def __init__(self):
        """Initialize APIManager with empty connector cache."""
        self._cache: dict = {}
        logger.info("APIManager initialized with %d connectors.", len(CONNECTOR_MODULE_MAP))

    def list_connectors(self) -> list:
        """Return list of all 100 connector names.

        Returns:
            List of connector name strings.
        """
        return list(CONNECTOR_MODULE_MAP.keys())

    def get_connector(self, name: str):
        """Load and return a connector instance by name.

        Args:
            name: Connector name (without '_connector' suffix).

        Returns:
            Instantiated connector object.

        Raises:
            ValueError: If connector name is not recognized.
        """
        if name in self._cache:
            logger.debug("APIManager returning cached connector: %s", name)
            return self._cache[name]
        if name not in CONNECTOR_MODULE_MAP:
            raise ValueError(f"Unknown connector: {name}. Available: {self.list_connectors()}")
        module_path, class_name = CONNECTOR_MODULE_MAP[name]
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instance = cls()
            self._cache[name] = instance
            logger.info("APIManager loaded connector: %s (%s)", name, class_name)
            return instance
        except Exception as e:
            logger.error("APIManager failed to load connector %s: %s", name, e)
            raise

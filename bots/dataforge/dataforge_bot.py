"""DataForge AI Bot - main orchestrator for dataset generation and selling."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bots.bot_base import BotBase
from bots.dataforge.dataset_generators.voice_dataset import VoiceDatasetGenerator
from bots.dataforge.dataset_generators.facial_dataset import FacialDatasetGenerator
from bots.dataforge.dataset_generators.item_dataset import ItemDatasetGenerator
from bots.dataforge.dataset_generators.behavioral_dataset import BehavioralDatasetGenerator
from bots.dataforge.dataset_generators.emotion_engine_dataset import EmotionEngineDatasetGenerator
from bots.dataforge.packaging.json_packager import JSONPackager
from bots.dataforge.packaging.csv_packager import CSVPackager
from bots.dataforge.packaging.wav_packager import WAVPackager
from bots.dataforge.packaging.coco_packager import COCOPackager
from bots.dataforge.packaging.jsonl_packager import JSONLPackager
from bots.dataforge.sales_channels import SalesChannels
from bots.dataforge.marketplace.huggingface_publisher import HuggingFacePublisher
from bots.dataforge.marketplace.kaggle_publisher import KagglePublisher
from bots.dataforge.marketplace.aws_publisher import AWSMarketplacePublisher
from bots.dataforge.marketplace.direct_api_seller import DirectAPISeller

logger = logging.getLogger(__name__)


class DataForgeBot(BotBase):
    """DataForge AI Bot: orchestrates data collection, generation, packaging, and selling.

    Inherits from BotBase and coordinates all dataset generators, packagers,
    sales channels, and marketplace publishers.
    """

    def __init__(self):
        """Initialize DataForgeBot with all sub-components."""
        super().__init__(bot_id="dataforge-001", bot_name="DataForge AI Bot")
        self.voice_gen = VoiceDatasetGenerator()
        self.facial_gen = FacialDatasetGenerator()
        self.item_gen = ItemDatasetGenerator()
        self.behavioral_gen = BehavioralDatasetGenerator()
        self.emotion_gen = EmotionEngineDatasetGenerator()
        self.json_packager = JSONPackager()
        self.csv_packager = CSVPackager()
        self.wav_packager = WAVPackager()
        self.coco_packager = COCOPackager()
        self.jsonl_packager = JSONLPackager()
        self.sales = SalesChannels()
        self._datasets: dict = {}

    def run(self):
        """Run the full DataForge pipeline.

        Returns:
            Dict with all collected and generated dataset data.
        """
        logger.info("DataForge AI Bot starting...")
        bot_data = self.collect_from_bots()
        synthetic = self.generate_synthetic_data()
        all_data = {**bot_data, **synthetic}
        self.package_datasets(all_data)
        self.list_for_sale()
        logger.info("DataForge AI Bot pipeline complete.")
        return all_data

    def collect_from_bots(self) -> dict:
        """Import all other bots and collect their structured data exports.

        Returns:
            Dict mapping bot names to their exported structured data.
        """
        collected = {}
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "government_contract_grant_bot",
                os.path.join(os.path.dirname(__file__), "..", "government-contract-grant-bot",
                             "government_contract_grant_bot.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            bot = module.GovernmentContractGrantBot()
            collected["government_contract_grant_bot"] = bot.export_structured_data()
            logger.info("Collected data from GovernmentContractGrantBot.")
        except Exception as e:
            logger.warning("Could not collect from GovernmentContractGrantBot: %s", e)
            collected["government_contract_grant_bot"] = {"type": "government", "content": [], "error": str(e)}
        return collected

    def generate_synthetic_data(self) -> dict:
        """Generate synthetic datasets using all 5 dataset generators.

        Returns:
            Dict with keys 'voice', 'facial', 'items', 'behavioral', 'emotion'.
        """
        logger.info("Generating synthetic datasets...")
        voice_data = self.voice_gen.generate(num_samples=100)
        facial_data = self.facial_gen.generate(num_samples=200)
        item_data = self.item_gen.generate(num_items=500)
        behavioral_data = self.behavioral_gen.generate(num_conversations=100)
        emotion_data = self.emotion_gen.generate(num_samples=200)
        self._datasets = {
            "voice": voice_data,
            "facial": facial_data,
            "items": item_data,
            "behavioral": behavioral_data,
            "emotion": emotion_data,
        }
        logger.info(
            "Generated: voice=%d facial=%d items=%d behavioral=%d emotion=%d",
            len(voice_data), len(facial_data), len(item_data), len(behavioral_data), len(emotion_data)
        )
        return self._datasets

    def package_datasets(self, datasets: dict = None) -> dict:
        """Package datasets using all 5 packagers.

        Args:
            datasets: Dict of datasets to package; uses self._datasets if None.

        Returns:
            Dict mapping package type to output file path.
        """
        import tempfile
        if datasets is None:
            datasets = self._datasets
        output_dir = tempfile.mkdtemp(prefix="dataforge_")
        packaged = {}
        voice = datasets.get("voice", [])
        if voice:
            path = self.wav_packager.pack(voice, output_dir)
            packaged["voice_wav"] = path
        facial = datasets.get("facial", [])
        if facial:
            path = self.coco_packager.pack(facial, os.path.join(output_dir, "facial_coco.json"))
            packaged["facial_coco"] = path
        items = datasets.get("items", [])
        if items:
            path = self.csv_packager.pack(items, os.path.join(output_dir, "items.csv"))
            packaged["items_csv"] = path
        behavioral = datasets.get("behavioral", [])
        if behavioral:
            path = self.jsonl_packager.pack(behavioral, os.path.join(output_dir, "behavioral.jsonl"))
            packaged["behavioral_jsonl"] = path
        emotion = datasets.get("emotion", [])
        if emotion:
            path = self.json_packager.pack(emotion, os.path.join(output_dir, "emotion.json"))
            packaged["emotion_json"] = path
        logger.info("Packaged %d datasets to %s", len(packaged), output_dir)
        return packaged

    def list_for_sale(self) -> dict:
        """List all datasets for sale across all sales channels.

        Returns:
            Dict mapping channel key to sale result dict.
        """
        voice = self._datasets.get("voice", [])
        facial = self._datasets.get("facial", [])
        behavioral = self._datasets.get("behavioral", [])
        results = {}
        results["huggingface_voice"] = self.sales.push_to_huggingface("voice-emotion-dataset", voice)
        results["huggingface_facial"] = self.sales.push_to_huggingface("facial-expression-dataset", facial)
        results["kaggle_behavioral"] = self.sales.push_to_kaggle("behavioral-ai-conversations", behavioral)
        results["aws_voice_bundle"] = self.sales.push_to_aws_marketplace("Voice Dataset Bundle", "voice_dataset_bundle")
        results["aws_facial"] = self.sales.push_to_aws_marketplace("Facial Synthetic Set", "facial_synthetic_set")
        results["aws_behavioral"] = self.sales.push_to_aws_marketplace("Behavioral AI Pack", "behavioral_ai_pack")
        results["direct_api"] = self.sales.sell_direct_api("emotion-engine-dataset", "api_subscription_monthly", "platform")
        logger.info("Listed datasets for sale on %d channels.", len(results))
        return results

    def export_structured_data(self) -> dict:
        """Export DataForge structured data summary for other bots.

        Returns:
            Structured data dict describing available datasets.
        """
        return {
            "type": "dataforge",
            "labels": ["voice", "facial", "behavioral", "emotion", "items"],
            "content": list(self._datasets.keys()),
            "consent": True,
            "anonymized": True,
            "license": "CC-BY-4.0",
            "datasets_available": {k: len(v) for k, v in self._datasets.items()},
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = DataForgeBot()
    bot.run()

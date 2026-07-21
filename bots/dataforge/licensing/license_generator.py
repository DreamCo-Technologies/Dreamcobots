"""License generator for DataForge AI datasets."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LicenseGenerator:
    """Generates dataset licenses for various use cases."""

    def generate_commercial(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a commercial use license.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Commercial license text string.
        """
        year = datetime.utcnow().year
        text = (
            f"COMMERCIAL LICENSE\n"
            f"Dataset: {dataset_name} | Version: {version}\n"
            f"Copyright (c) {year} DataForge AI Systems\n\n"
            "Permission is hereby granted to use, copy, modify, merge, publish, distribute,\n"
            "sublicense, and/or sell copies of this dataset and derivatives for commercial purposes,\n"
            "subject to the following conditions:\n"
            "- Attribution must be given to DataForge AI Systems.\n"
            "- This license notice must be included in all copies.\n\n"
            "License: CC-BY-4.0 | https://creativecommons.org/licenses/by/4.0/"
        )
        logger.info("Commercial license generated for %s v%s", dataset_name, version)
        return text

    def generate_non_commercial(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a non-commercial use license.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Non-commercial license text string.
        """
        year = datetime.utcnow().year
        text = (
            f"NON-COMMERCIAL LICENSE\n"
            f"Dataset: {dataset_name} | Version: {version}\n"
            f"Copyright (c) {year} DataForge AI Systems\n\n"
            "This dataset may be used, copied, and modified for NON-COMMERCIAL purposes only.\n"
            "Commercial use of this dataset or its derivatives is strictly prohibited.\n\n"
            "License: CC-BY-NC-4.0 | https://creativecommons.org/licenses/by-nc/4.0/"
        )
        logger.info("Non-commercial license generated for %s v%s", dataset_name, version)
        return text

    def generate_research_only(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a research-only use license.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Research-only license text string.
        """
        year = datetime.utcnow().year
        text = (
            f"RESEARCH-ONLY LICENSE\n"
            f"Dataset: {dataset_name} | Version: {version}\n"
            f"Copyright (c) {year} DataForge AI Systems\n\n"
            "This dataset is licensed for academic and non-profit research use only.\n"
            "Any commercial use, redistribution, or modification for commercial products is prohibited.\n"
            "Publications using this dataset must cite DataForge AI Systems.\n\n"
            "License: CC-BY-NC-ND-4.0 | https://creativecommons.org/licenses/by-nc-nd/4.0/"
        )
        logger.info("Research-only license generated for %s v%s", dataset_name, version)
        return text

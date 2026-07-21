"""Ingestion sub-package: scrapers and dataset normalisation."""

from .paper_scraper import PaperScraper
from .github_scraper import GitHubScraper
from .kaggle_scraper import KaggleScraper
from .dataset_normalizer import DatasetNormalizer

__all__ = ["PaperScraper", "GitHubScraper", "KaggleScraper", "DatasetNormalizer"]

"""
DreamCo Divisions — shared data and utilities.

This package provides:
  - JSON bot catalogues for each division (DreamRealEstate, DreamSalesPro, …)
  - RevenueSimulator: unified revenue simulation engine

Usage
-----
    from divisions.revenue_simulator import RevenueSimulator
"""
# GLOBAL AI SOURCES FLOW

from divisions.revenue_simulator import RevenueSimulator

__all__ = ["RevenueSimulator"]

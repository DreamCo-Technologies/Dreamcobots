"""Tests for bots/home_buyer_bot/contract_generator.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.home_buyer_bot.contract_generator import ContractGenerator, Contract


# ---------------------------------------------------------------------------
# generate_contract
# ---------------------------------------------------------------------------

class TestGenerateContract:
    def setup_method(self):
        self.gen = ContractGenerator()

    def test_returns_contract(self):
        contract = self.gen.generate_contract(
            buyer="DreamCo LLC",
            seller="John Smith",
            property_address="123 Main St, Chicago IL",
            price=45_000,
        )
        assert isinstance(contract, Contract)

    def test_contract_id_generated(self):
        contract = self.gen.generate_contract("B", "S", "Addr", 50_000)
        assert contract.contract_id.startswith("DC-")

    def test_text_contains_buyer(self):
        contract = self.gen.generate_contract("DreamCo LLC", "John", "123 Oak", 30_000)
        assert "DreamCo LLC" in contract.text

    def test_text_contains_seller(self):
        contract = self.gen.generate_contract("Buyer", "Seller Name", "456 Elm", 40_000)
        assert "Seller Name" in contract.text

    def test_text_contains_address(self):
        contract = self.gen.generate_contract("B", "S", "789 Pine Ave, IL", 25_000)
        assert "789 Pine Ave, IL" in contract.text

    def test_text_contains_price(self):
        contract = self.gen.generate_contract("B", "S", "Addr", 75_000)
        assert "75,000.00" in contract.text

    def test_not_signed_by_default(self):
        contract = self.gen.generate_contract("B", "S", "Addr", 10_000)
        assert contract.signed is False

    def test_stored_in_list(self):
        self.gen.generate_contract("B", "S", "Addr1", 10_000)
        self.gen.generate_contract("B", "S", "Addr2", 20_000)
        contracts = self.gen.list_contracts()
        assert len(contracts) == 2


# ---------------------------------------------------------------------------
# get_contract
# ---------------------------------------------------------------------------

class TestGetContract:
    def test_get_existing_contract(self):
        gen = ContractGenerator()
        contract = gen.generate_contract("B", "S", "Addr", 10_000)
        found = gen.get_contract(contract.contract_id)
        assert found is not None
        assert found.contract_id == contract.contract_id

    def test_get_nonexistent_returns_none(self):
        gen = ContractGenerator()
        assert gen.get_contract("DC-NOTEXIST") is None


# ---------------------------------------------------------------------------
# mark_signed
# ---------------------------------------------------------------------------

class TestMarkSigned:
    def test_mark_signed_returns_true(self):
        gen = ContractGenerator()
        contract = gen.generate_contract("B", "S", "Addr", 10_000)
        result = gen.mark_signed(contract.contract_id)
        assert result is True
        assert gen.get_contract(contract.contract_id).signed is True

    def test_mark_nonexistent_returns_false(self):
        gen = ContractGenerator()
        assert gen.mark_signed("DC-INVALID") is False


# ---------------------------------------------------------------------------
# list_contracts
# ---------------------------------------------------------------------------

class TestListContracts:
    def test_empty_list(self):
        gen = ContractGenerator()
        assert gen.list_contracts() == []

    def test_to_dict_has_keys(self):
        gen = ContractGenerator()
        gen.generate_contract("B", "S", "Addr", 10_000)
        contracts = gen.list_contracts()
        d = contracts[0]
        for key in ("contract_id", "buyer", "seller", "property_address", "price", "signed"):
            assert key in d

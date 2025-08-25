import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock
import datetime
import pytest

fake_model = MagicMock()
fake_model.predict.return_value = [0]
fake_model.predict_proba.return_value = [[0.0, 0.1]]

fake_scaler = MagicMock()
fake_scaler.transform.return_value = [[0.0]]

import app.settings.algorithm_models as alg_mod
alg_mod.load_model = lambda: fake_model
alg_mod.load_scaler = lambda: fake_scaler

from app.service.transaction_service import TransactionService


@pytest.mark.parametrize(
    "card,expected",[
        ("1234567890123456", "************3456"), 
        ("0000", "0000"),                          
    ]
)
def test_mask_card_basic(card, expected):
    assert TransactionService.mask_card(card) == expected


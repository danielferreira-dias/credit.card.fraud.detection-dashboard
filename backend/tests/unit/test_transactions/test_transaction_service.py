import pytest
from app.service.transaction_service import TransactionService

@pytest.mark.parametrize(
    "card,expected",[
        ("1234567890123456", "************3456"), 
        ("0000", "0000"),                          
    ]
)
def test_mask_card_basic(card, expected):
    assert TransactionService.mask_card(card) == expected


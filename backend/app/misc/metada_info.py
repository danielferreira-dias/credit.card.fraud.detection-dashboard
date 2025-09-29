# Initial metadata for new conversation
from datetime import datetime

initial_metadata = {
    "session_info": {
        "session_start": datetime.now().isoformat(),
        "session_type": "investigation",
        "user_agent": "web_client",
        "initial_connection": True
    },
    "investigated_entities": {
        "transaction_ids": [],
        "customer_ids": [],
        "merchant_names": [],
        "countries": [],
        "card_types": []
    },
    "tools_used": [],
    "investigation_summary": {
        "fraud_cases_found": 0,
        "total_amount_investigated": 0.0,
        "risk_levels_analyzed": [],
        "investigation_outcome": "in_progress"
    },
    "session_stats": {
        "total_queries": 0,
        "tools_executed": 0,
        "errors_encountered": 0
    },
    "tags": [],
    "investigation_priority": "medium",
    "conversation_context": {
        "title_generated": False,
        "auto_title": None,
        "user_provided_title": None
    }
}
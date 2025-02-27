import json
import logging
from typing import Any, Dict

with open("app/api/v1/logging.json", "r", encoding="utf-8") as f:
    API_LOG_CONFIG: Dict[str, Any] = json.load(f)

logger = logging.getLogger("monopoly")

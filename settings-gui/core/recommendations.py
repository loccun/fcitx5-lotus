# SPDX-FileCopyrightText: 2026 Nguyen Hoang Ky <nhktmdzhg@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Recommendation engine for per-application input modes.
This module helps users choose the best input mode for specific applications.
"""

import re

# Mode constants (should match mode_manager.py and C++ LotusEngine)
MODE_OFF = 0
MODE_SMOOTH = 1
MODE_SLOW = 2
MODE_HARDCORE = 3
MODE_SURROUNDING = 4
MODE_PREEDIT = 5
MODE_EMOJI = 6
MODE_DEFAULT = -1

# USER: Group recommendations by category for better readability.
# Status values: "good" (Recommended), "bad" (Poor compatibility)
APP_RECOMMENDATIONS = {
    "Firefox-based": {
        "pattern": r"firefox|librewolf|waterfox|floorp|zen",
        "recommendations": {
            MODE_SMOOTH: "good",
            MODE_SLOW: "good",
            MODE_HARDCORE: "good",
            MODE_SURROUNDING: "good",
            MODE_PREEDIT: "good",
        }
    },
    "Chromium-based": {
        "pattern": r"chrome|chromium|brave|vivaldi|opera|edge",
        "recommendations": {
            MODE_SMOOTH: "good",
            MODE_SLOW: "good",
            MODE_HARDCORE: "good",
            MODE_SURROUNDING: "bad",
            MODE_PREEDIT: "good",
        }
    }
}

def get_recommendation(app_name: str, mode: int) -> str:
    """
    Looks up a recommendation status for a given app and mode.
    Returns: "good", "bad", or None
    """
    if not app_name:
        return None
        
    app_lower = app_name.lower()
    
    for category, data in APP_RECOMMENDATIONS.items():
        if re.search(data["pattern"], app_lower):
            return data["recommendations"].get(mode)
            
    return None

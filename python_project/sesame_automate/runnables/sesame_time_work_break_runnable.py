from datetime import datetime
import logging
import os
import traceback
from typing import Any, Dict, Optional, override
import requests
from sesame_automate.models.runnable_sequence import Runnable

class SesameTimeWorkBreakRunnable(Runnable):
    
    def __init__(self):
        self._base_url = os.getenv("BASE_URL")
        self._work_break_endpoint = "/api/v3/companies/{0}/work-breaks"
        self._logger = logging.getLogger(__name__)

    @override
    def execute(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not data or not data.get('login_successful'):
            return {
                'last_successful': False,
                'error': 'Login failed, cannot proceed with work break',
                'previous_error': data.get('error') if data else None
            }
        
        try:
            work_break_info = self._work_break(data['session'], data.get("user_info", {}).get("company_id"))
            if work_break_info and data.get("is_welcome", False):
                self._logger.info(f"Work break '{work_break_info.get('name')}' found with ID: {work_break_info.get('id')}")

            return {
                'last_successful': True,
                'timestamp': datetime.now().isoformat(),
                "work_break_id": work_break_info.get("id") if work_break_info else None
            }
        except Exception as e:
            return {
                'last_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _work_break(self, session: requests.Session, company_id: Optional[str] = None) -> None:
        if not self._base_url:
            raise ValueError("Please set BASE_URL in your environment variables.")
        
        if not company_id:
            raise ValueError("Company ID is required to fetch work break info")
        
        work_break_url = self._base_url + self._work_break_endpoint.format(company_id)
        
        response = session.get(work_break_url)
        response.raise_for_status()
        response = response.json()
        if len(response.get("data",[])) == 0:
            raise ValueError("Failed to retrieve work break info")
        work_break_info = filter(lambda wb: wb.get("name") == os.getenv("BREAK_NAME"), response.get("data",[]))
        return next(work_break_info, None)

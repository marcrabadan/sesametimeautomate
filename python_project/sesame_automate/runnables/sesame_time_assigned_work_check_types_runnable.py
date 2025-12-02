from datetime import datetime
import logging
import os
import traceback
from typing import Any, Dict, Optional, override
import requests
from sesame_automate.models.runnable_sequence import Runnable

class SesameTimeAssignedWorkCheckTypesRunnable(Runnable):
    def __init__(self):
        self._base_url = os.getenv("BASE_URL")
        self._check_types_endpoint = "/api/v3/employees/{0}/assigned-work-check-types"
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
            check_types = self._check_types(data['session'], data.get("user_info", {}).get("user_id"))
            if data.get("is_welcome", False) and len(check_types) > 0:
                self._logger.info("Assigned Work Check types retrieved:")
                for ct in check_types:
                    self._logger.info(f"Check type '{ct.get('name')}'")
            
            return {
                'last_successful': True,
                'timestamp': datetime.now().isoformat(),
                "check_types": check_types
            }
        except Exception as e:
            traceback.print_exc()
            self._logger.error(f"Failed to fetch check types: {e}")
            return {
                'last_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
    def _check_types(self, session: requests.Session, employee_id: Optional[str] = None) -> list:
        if not self._base_url:
            raise ValueError("Please set BASE_URL in your environment variables.")
        
        check_types_url = self._base_url + self._check_types_endpoint.format(employee_id)
        
        response = session.get(check_types_url)
        response.raise_for_status()
        response = response.json()
        return response.get("data",[])

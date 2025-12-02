from datetime import datetime
import json
import logging
import os
import traceback
from sesame_automate.models.enums.state import State
from typing import Any, Dict, Optional, override
import requests
from sesame_automate.models.runnable_sequence import Runnable
from builtins import filter

class SesameTimeCheckInRunnable(Runnable):
    def __init__(self):
        self._base_url = os.getenv("BASE_URL")
        self._check_in_endpoint = "/api/v3/employees/{}/check-in"
        self._logger = logging.getLogger(__name__)

    @override
    def execute(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not data or not data.get('login_successful'):
            return {
                'last_successful': False,
                'error': 'Login failed, cannot proceed with check-in',
                'previous_error': data.get('error') if data else None
            }
        
        try:
            self._check_in(data)
            return {
                'last_successful': True,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self._logger.error(f"Check-in failed: {str(e)}")
            traceback.print_exc()   
            return {
                'last_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_in(self, data: dict[str, Any]) -> None:
        if not self._base_url:
            raise ValueError("Please set BASE_URL in your environment variables.")
        session: requests.Session = data['session']
        user_id: Optional[str] = data.get("user_info", {}).get("user_id")
        if not user_id:
            raise ValueError("User ID is required to perform check-in")
        current_state: State = data.get("current_state", State.UNKNOWN)
        if current_state == State.UNKNOWN:
            raise ValueError("Current state is unknown, cannot perform check-in")
        
        check_in_url = self._base_url + self._check_in_endpoint.format(user_id)
        
        headers = {'Content-Type': 'application/json'}
        
        work_check_type_id: Optional[str] = None
        if current_state == State.BREAK:
            work_check_type_id = data.get("work_break_id")
            self._logger.info("Performing check-in BREAK")
        elif current_state == State.WORKING:
            if os.getenv("REMOTE_WORK_DAYS") != "" and datetime.now().strftime("%A") in os.getenv("REMOTE_WORK_DAYS", "").split(","):
                check_types = data.get("check_types", [])
                remote_checks = [x for x in check_types if x.get("workType") == "remote" and x.get("status") == "active"]
                if len(remote_checks) == 0:
                    raise ValueError("No remote work check type found")
                self._logger.info("Performing check-in REMOTE")
                work_check = remote_checks[0]
                work_check_type_id = work_check.get("id")
            else:
                self._logger.info("Performing check-in NORMAL")
                work_check_type_id = None

        payload = {
            "coordinates": {},
            "origin": "web",
            "workCheckTypeId" : work_check_type_id
        }

        self._logger.info(f"Trying check in")
        
        response = session.post(check_in_url, json=payload, headers=headers)
        response.raise_for_status()
        
        self._logger.info(f"Check-in successful at {datetime.now()}")

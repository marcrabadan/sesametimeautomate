import logging
import os
import traceback
from typing import Any, Dict, override
import requests
from sesame_automate.models.runnable_sequence import Runnable

class SesameTimeMeInfoRunnable(Runnable):
    def __init__(self):
        self._base_url = os.getenv("BASE_URL")
        self._me_info_endpoint = "/api/v3/security/me"
        self._logger = logging.getLogger(__name__)
        
    @override
    def execute(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not data or not data.get('login_successful'):
            return {
                'last_successful': False,
                'error': 'Login failed, cannot fetch user info',
                'previous_error': data.get('error') if data else None
            }
        
        try:
            user_info = self._fetch_me_info(data['session'])
            
            if len(user_info.get("data",[])) == 0:
                return {
                    'last_successful': False,
                    'error': 'Failed to retrieve user info'
                }
            user_info = user_info.get("data",[])[0]

            if data.get("is_welcome", False):
                self._logger.info(f"User info retrieved for {user_info.get('firstName')} {user_info.get('lastName')} in company {user_info.get('companyName')}")
            
            return {
                'last_successful': True,
                'user_info': {
                    "company_id": user_info.get('companyId'),
                    "user_id": user_info.get('id'),
                    "full_name": user_info.get('firstName') + ' ' + user_info.get('lastName'),
                    "company_name": user_info.get('companyName')
                }
            }
        except Exception as e:
            self._logger.error(f"Failed to fetch user info: {e}")
            return {
                'last_successful': False,
                'error': str(e)
            }
    
    def _fetch_me_info(self, session: requests.Session) -> Dict[str, Any]:
        if not self._base_url:
            raise ValueError("Please set BASE_URL in your environment variables.")
        
        me_info_url = self._base_url + self._me_info_endpoint
        
        response = session.get(me_info_url)
        response.raise_for_status()
        
        return response.json()


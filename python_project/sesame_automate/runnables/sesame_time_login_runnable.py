import logging
import os
import traceback
from typing import Any, Dict, override
import requests
from sesame_automate.models.runnable_sequence import Runnable


class SesameTimeLoginRunnable(Runnable):

    def __init__(self):
        self.session = requests.Session()
        self._base_url = os.getenv("BASE_URL")
        self._login_url = "/api/v3/security/login"
        self._email = os.getenv("SESAME_EMAIL")
        self._password = os.getenv("SESAME_PASSWORD")
        self._logger = logging.getLogger(__name__)
        
    @override
    def execute(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            self._login()
            return {
                'session': self.session,
                'login_successful': True
            }
        except Exception as e:
            self._logger.error(f"Login failed: {e}")
            self._logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'session': None,
                'login_successful': False,
                'error': str(e)
            }
    
    def _login(self) -> None:
        
        if not self._base_url or not self._login_url:
            raise ValueError("Please set BASE_URL and LOGIN_URL in your environment variables.")
        if not self._email or not self._password:
            raise ValueError("Please set SESAME_EMAIL and SESAME_PASSWORD in your environment variables.")
        
        full_login_url = self._base_url + self._login_url
        
        payload = {
            "platformData": {
                "platformName": "Chrome",
                "platformSystem": "Mac/iOS",
                "platformVersion": "142"
            },
            "email": self._email,
            "password": self._password
        }
        
        response = self.session.post(full_login_url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        if 'data' in response_data:
            session_id = response_data['data']
            from datetime import datetime, timedelta
            expires = datetime.now() + timedelta(days=365)
            expires_ts = int(expires.timestamp())
            
            self.session.cookies.set(
                name='USID',
                value=session_id,
                domain=os.getenv("COOKIE_DOMAIN"),
                path='/',
                expires=expires_ts
            )
            
            self._logger.info(f"Login successful at {datetime.now()}")
        else:
            raise ValueError("Unexpected response format: 'data' field not found")

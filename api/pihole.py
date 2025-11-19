"""Pi-hole API client for v6"""

import requests
from config import PIHOLE_API, PIHOLE_PASSWORD


class PiholeAPI:
    """Pi-hole API v6 client"""

    def __init__(self) -> None:
        self.base_url = PIHOLE_API
        self.session_id = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Pi-hole API"""
        if not PIHOLE_PASSWORD:
            return
        try:
            response = requests.post(
                f"{self.base_url}/auth",
                json={"password": PIHOLE_PASSWORD},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session", {}).get("sid")
        except Exception as e:
            print(f"Auth error: {e}")

    def _get(self, endpoint: str) -> dict:
        """Make authenticated GET request"""
        headers: dict[str, str] = {}
        if self.session_id:
            headers["sid"] = self.session_id

        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=5,
            )
            if response.status_code == 401:
                self._authenticate()
                headers["sid"] = self.session_id
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    timeout=5,
                )
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            print(f"API error: {e}")
            return {}

    def get_summary(self) -> dict:
        """Get Pi-hole summary statistics"""
        data = self._get("/stats/summary")
        queries = data.get("queries", {})
        clients = data.get("clients", {})
        return {
            "dns_queries_today": queries.get("total", 0),
            "ads_blocked_today": queries.get("blocked", 0),
            "ads_percentage_today": queries.get("percent_blocked", 0),
            "unique_clients": clients.get("active", 0),
            "domains_being_blocked": data.get("gravity", {}).get("domains_being_blocked", 0),
            "status": "enabled" if data.get("blocking", True) else "disabled",
        }

    def get_overtime(self) -> dict:
        """Get query overtime data for graphs"""
        return self._get("/history")

    def get_top_blocked(self, count: int = 10) -> dict:
        """Get top blocked domains"""
        data = self._get(f"/stats/top_domains?blocked=true&count={count}")

        # Convert list to dict format
        result = {}
        for item in data.get("domains", []):
            result[item.get("domain", "unknown")] = item.get("count", 0)
        return {"domains": result}

    def get_top_clients(self, count: int = 10) -> dict:
        """Get top clients"""
        data = self._get(f"/stats/top_clients?count={count}")

        # Convert list to dict format
        result = {}
        for item in data.get("clients", []):
            name = item.get("name") or item.get("ip", "unknown")
            result[name] = item.get("count", 0)
        return {"clients": result}

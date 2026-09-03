import json
import os
import time
import requests

class MicrosoftAuth:

    DEFAULT_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    DEVICE_CODE_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
    TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    SCOPE = "XboxLive.signin offline_access"

    def __init__(self, client_id=None, cache_file="msa.json", log_func=print):
        self.client_id = client_id or self.DEFAULT_CLIENT_ID
        self.cache_file = cache_file
        self.log = log_func
        self.cache = {}
        self._load_cache()

    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception:
            self.cache = {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def login(self):
        mc_token = self.cache.get("mc_token")
        mc_expiry = self.cache.get("mc_expiry", 0)
        if mc_token and time.time() < mc_expiry - 60 and self.cache.get("uuid"):
            return {
                "access_token": mc_token,
                "uuid": self.cache["uuid"],
                "name": self.cache["name"]
            }

        msa_token = self._get_msa_token()
        xbl_token, uhs = self._xbl_auth(msa_token)
        xsts_token, uhs = self._xsts_auth(xbl_token)
        mc_token = self._mc_token(xsts_token, uhs)
        profile = self._profile(mc_token)

        self.cache["mc_token"] = mc_token
        self.cache["mc_expiry"] = time.time() + self.cache.get("mc_expires_in", 86400)
        self.cache["uuid"] = profile["id"]
        self.cache["name"] = profile["name"]
        self._save_cache()

        return {
            "access_token": mc_token,
            "uuid": profile["id"],
            "name": profile["name"]
        }

    def join_server(self, server_hash):
        token = self.cache.get("mc_token")
        uuid = self.cache.get("uuid")
        if not token or not uuid:
            raise Exception("Not logged in to Microsoft account")
        resp = requests.post(
            "https://sessionserver.mojang.com/session/minecraft/join",
            json={
                "accessToken": token,
                "selectedProfile": uuid.replace('-', ''),
                "serverId": server_hash
            },
            timeout=15
        )
        if resp.status_code != 204:
            raise Exception(f"Session verification failed: HTTP {resp.status_code} {resp.text[:200]}")

    def _get_msa_token(self):
        refresh_token = self.cache.get("refresh_token")
        if refresh_token:
            try:
                return self._refresh_flow(refresh_token)
            except Exception:
                pass
        return self._device_flow()

    def _device_flow(self):
        r = requests.post(self.DEVICE_CODE_URL, data={
            "client_id": self.client_id,
            "scope": self.SCOPE
        }, timeout=15).json()

        self.log("=" * 50)
        self.log("Microsoft account login required (first login or expired)")
        self.log(f"1. Open browser: {r.get('verification_uri', 'https://www.microsoft.com/link')}")
        self.log(f"2. Enter code: {r.get('user_code', '')}")
        self.log("=" * 50)

        interval = r.get("interval", 5)
        expires = time.time() + r.get("expires_in", 900)
        while time.time() < expires:
            time.sleep(interval)
            tj = requests.post(self.TOKEN_URL, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": self.client_id,
                "device_code": r["device_code"]
            }, timeout=15).json()

            if "access_token" in tj:
                self.cache["refresh_token"] = tj.get("refresh_token")
                self._save_cache()
                return tj["access_token"]
            err = tj.get("error")
            if err == "authorization_pending":
                continue
            if err == "slow_down":
                interval += 5
                continue
            raise Exception(f"Microsoft login failed: {err} - {tj.get('error_description', '')[:200]}")
        raise Exception("Microsoft login timed out, please retry")

    def _refresh_flow(self, refresh_token):
        tj = requests.post(self.TOKEN_URL, data={
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
            "scope": self.SCOPE
        }, timeout=15).json()
        if "access_token" not in tj:
            raise Exception("Failed to refresh token")
        if tj.get("refresh_token"):
            self.cache["refresh_token"] = tj["refresh_token"]
            self._save_cache()
        return tj["access_token"]

    def _xbl_auth(self, msa_token):
        r = requests.post(
            "https://user.auth.xboxlive.com/user/authenticate",
            json={
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": "d=" + msa_token
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            },
            timeout=15
        ).json()
        return r["Token"], r["DisplayClaims"]["xui"][0]["uhs"]

    def _xsts_auth(self, xbl_token):
        r = requests.post(
            "https://xsts.auth.xboxlive.com/xsts/authorize",
            json={
                "Properties": {
                    "SandboxId": "RETAIL",
                    "UserTokens": [xbl_token]
                },
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT"
            },
            timeout=15
        )
        if r.status_code == 401:
            err = r.json().get("XErr")
            if err == 2148916233:
                raise Exception("This Microsoft account does not have a Minecraft (Java Edition) profile")
            if err == 2148916238:
                raise Exception("This account is a child account and cannot log in")
            raise Exception(f"XSTS authentication failed: XErr {err}")
        r.raise_for_status()
        j = r.json()
        return j["Token"], j["DisplayClaims"]["xui"][0]["uhs"]

    def _mc_token(self, xsts_token, uhs):
        r = requests.post(
            "https://api.minecraftservices.com/authentication/login_with_xbox",
            json={"identityToken": f"XBL3.0 x={uhs};{xsts_token}"},
            timeout=15
        ).json()
        if "access_token" not in r:
            raise Exception(f"Failed to get Minecraft token: {str(r)[:200]}")
        self.cache["mc_expires_in"] = r.get("expires_in", 86400)
        return r["access_token"]

    def _profile(self, mc_token):
        r = requests.get(
            "https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": "Bearer " + mc_token},
            timeout=15
        )
        if r.status_code != 200:
            raise Exception("This account does not own Minecraft Java Edition (cannot fetch profile)")
        p = r.json()
        if not p.get("name"):
            raise Exception("Profile is empty, please create a username on the official website first")
        return p

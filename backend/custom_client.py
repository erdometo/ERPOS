import os
import json
import uuid
import urllib.request
import urllib.error
from typing import Any, List, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class ChatCustom(BaseChatModel):
    client_id: str
    client_secret: str
    base_url: str = os.getenv("CUSTOM_BASE_URL", "")
    model_name: str = "gemini-3-flash"
    temperature: float = 0.1
    _token: Optional[str] = None
    _model_mapping: Dict[str, str] = {}

    def __init__(self, client_id: str, client_secret: str, model_name: str = "gemini-3-flash", temperature: float = 0.1, **kwargs):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            model_name=model_name,
            temperature=temperature,
            **kwargs
        )
        self._authenticate()
        self._load_models()

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _authenticate(self):
        url = f"{self.base_url}/auth/appLogin"
        payload = {"id": self.client_id, "secret": self.client_secret}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode("utf-8"))
                self._token = res.get("token")
        except Exception as e:
            raise ValueError(f"Custom LLM Authentication failed: {e}")

    def _load_models(self):
        if not self._token:
            self._authenticate()
        url = f"{self.base_url}/chat/models"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            },
            method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                models_list = json.loads(response.read().decode("utf-8"))
                mapping = {}
                for m in models_list:
                    # Map display name and deployment name to model UUID
                    name = m.get("name")
                    dep_name = m.get("deploymentName")
                    m_id = m.get("id")
                    if name:
                        mapping[name.lower()] = m_id
                    if dep_name:
                        mapping[dep_name.lower()] = m_id
                self._model_mapping = mapping
        except Exception as e:
            # Non-blocking warning: fall back to a known working model ID
            print(f"Warning: Failed to fetch Custom LLM models inventory: {e}")
            self._model_mapping = {}

    def _get_model_id(self) -> str:
        name_lower = self.model_name.lower().replace(" ", "").replace("-", "").replace("_", "")
        
        # Check exact mapped names first (after removing special characters for matching)
        normalized_mapping = {}
        for k, v in self._model_mapping.items():
            norm_k = k.replace(" ", "").replace("-", "").replace("_", "")
            normalized_mapping[norm_k] = v

        if name_lower in normalized_mapping:
            return normalized_mapping[name_lower]

        # Fuzzy lookup: check if requested name is substring or vice versa
        for k, v in normalized_mapping.items():
            if name_lower in k or k in name_lower:
                return v

        # Fallbacks:
        # If user requested a Gemini model and it was not found, prioritize higher versions:
        # 1. Look for gemini-3 first
        # 2. Then gemini-2.5
        # 3. Then any gemini
        if "gemini" in name_lower:
            def get_gemini_priority(key: str) -> int:
                score = 0
                if "gemini3" in key:
                    score += 10
                elif "gemini2.5" in key or "gemini25" in key:
                    score += 5
                elif "gemini2.0" in key or "gemini20" in key:
                    score += 2
                else:
                    score += 1
                
                # Tier matching: prioritize flash if requested flash, pro if requested pro
                if "flash" in name_lower and "flash" in key:
                    score += 2
                elif "pro" in name_lower and "pro" in key:
                    score += 2
                return score

            gemini_keys = [k for k in normalized_mapping.keys() if "gemini" in k]
            if gemini_keys:
                gemini_keys.sort(key=get_gemini_priority, reverse=True)
                return normalized_mapping[gemini_keys[0]]

        # Default fallback to Gemini 3 Flash UUID
        return "9fae2ed4-be69-4aed-8d89-cb21ad3dbaa0"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if not self._token:
            self._authenticate()

        # Convert LangChain messages to the Custom LLM payload format
        custom_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                role = "system"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                role = "user"
            custom_messages.append({"role": role, "content": msg.content})

        model_id = self._get_model_id()
        chat_id = str(uuid.uuid4())
        
        url = f"{self.base_url}/chat"
        payload = {
            "id": chat_id,
            "modelId": model_id,
            "messages": custom_messages,
            "stream": False,
            "temperature": self.temperature
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode("utf-8"))
                content = res.get("content", "")
                ai_message = AIMessage(content=content)
                generation = ChatGeneration(message=ai_message)
                return ChatResult(generations=[generation])
        except urllib.error.HTTPError as e:
            # Token expiration recovery: re-authenticate and retry
            if e.code == 403 or e.code == 401:
                self._authenticate()
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as retry_response:
                    res = json.loads(retry_response.read().decode("utf-8"))
                    content = res.get("content", "")
                    ai_message = AIMessage(content=content)
                    generation = ChatGeneration(message=ai_message)
                    return ChatResult(generations=[generation])
            error_body = e.read().decode("utf-8")
            raise ValueError(f"Custom LLM API call failed: {e.code} {e.reason} - {error_body}")
        except Exception as e:
            raise ValueError(f"Custom LLM API call failed: {e}")

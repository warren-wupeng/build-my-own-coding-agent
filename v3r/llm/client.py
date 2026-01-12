"""LLM Client for chat completions - Business concept abstraction"""

import json
import os
import sys
import urllib.request
import urllib.error


class LLMClient:
    """Large Language Model Client - Business concept abstraction"""

    def __init__(self,
                 provider="openrouter",
                 model="deepseek/deepseek-v3.2",
                 base_url="https://openrouter.ai/api/v1/chat/completions",
                 timeout=60,
                 max_tokens=4096):
        """
        Initialize LLM client

        Args:
            provider: LLM provider identifier (default: openrouter)
            model: Model identifier to use
            base_url: API endpoint URL
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens in response
        """
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.credentials = self._load_credentials()

    def generate(self, messages, tools=None):
        """
        Generate AI response from messages and available tools

        Args:
            messages: List of conversation messages
            tools: List of tool definitions (optional)

        Returns:
            API response as dictionary

        Raises:
            SystemExit: If API key is missing
            urllib.error.HTTPError: If API call fails
            Exception: For other errors
        """
        self._validate_credentials()
        prompt_data = self._prepare_prompt(messages, tools)
        response = self._make_request(prompt_data)
        return self._parse_response(response)

    def generate_with_tools(self, messages, tools):
        """
        Generate AI response with tool calling capability

        Args:
            messages: List of conversation messages
            tools: List of tool definitions

        Returns:
            API response as dictionary
        """
        return self.generate(messages, tools)

    def _load_credentials(self):
        """
        Load credentials for current provider

        Returns:
            API key string

        Raises:
            SystemExit: If API key is not set
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ Error: OPENROUTER_API_KEY environment variable not set")
            print("Please run: export OPENROUTER_API_KEY=\"your-key-here\"")
            print("Get API key: https://openrouter.ai/keys")
            sys.exit(1)
        return api_key

    def _validate_credentials(self):
        """Validate that credentials are set"""
        if not self.credentials:
            self.credentials = self._load_credentials()

    def _prepare_prompt(self, messages, tools):
        """
        Prepare prompt data for LLM generation

        Args:
            messages: List of conversation messages
            tools: List of tool definitions

        Returns:
            Dictionary with prompt data
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens
        }
        if tools:
            payload["tools"] = tools
        return payload

    def _make_request(self, prompt_data):
        """
        Make request to LLM provider

        Args:
            prompt_data: Prompt data dictionary

        Returns:
            HTTP response object

        Raises:
            urllib.error.HTTPError: If HTTP error occurs
            Exception: For other errors
        """
        # Convert to JSON bytes
        data = json.dumps(prompt_data).encode('utf-8')

        # Create request
        req = urllib.request.Request(
            self.base_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.credentials}",
                "Content-Type": "application/json"
            }
        )

        try:
            return urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ API call failed ({e.code}): {error_body}")
            raise
        except Exception as e:
            print(f"❌ API call failed: {e}")
            raise

    def _parse_response(self, response):
        """
        Parse response from LLM provider

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response as dictionary
        """
        return json.loads(response.read().decode('utf-8'))

    @classmethod
    def get_configuration_help(cls):
        """
        Get configuration help information for the LLM client

        Returns:
            List of configuration help strings
        """
        return [
            "⚙️  Configuration:",
            "   export OPENROUTER_API_KEY=\"your-api-key\"",
            "   Get API key: https://openrouter.ai/keys",
            ""
        ]

    @classmethod
    def from_env(cls):
        """
        Create client instance from environment variables

        Environment variables:
            OPENROUTER_MODEL: Model identifier (default: deepseek/deepseek-v3.2)
            OPENROUTER_TIMEOUT: Request timeout in seconds (default: 60)
            OPENROUTER_MAX_TOKENS: Maximum tokens (default: 4096)

        Returns:
            LLMClient instance
        """
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")
        timeout = int(os.getenv("OPENROUTER_TIMEOUT", "60"))
        max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))
        return cls(model=model, timeout=timeout, max_tokens=max_tokens)

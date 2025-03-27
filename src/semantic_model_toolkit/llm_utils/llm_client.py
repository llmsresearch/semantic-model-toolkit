"""Client for interacting with various LLM providers."""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

from loguru import logger
from snowflake.connector import SnowflakeConnection

from semantic_model_toolkit.core.config import LLMConfig


class LLMClient(ABC):
    """Abstract base class for LLM client implementations."""
    
    @abstractmethod
    def generate_description(self, context: str, prompt: str) -> str:
        """
        Generate a description using the LLM.
        
        Args:
            context (str): Context information to include in the prompt
            prompt (str): The prompt template to use
            
        Returns:
            str: The generated description
        """
        pass


class CortexLLMClient(LLMClient):
    """Client for Snowflake Cortex LLM."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the Cortex LLM client.
        
        Args:
            config: LLM configuration
        """
        self.model = config.model
        self._conn = None  # Will be set when connecting to Snowflake
        self.timeout = 30  # Set a default timeout of 30 seconds
        logger.info(f"Initialized Cortex LLM client with model: {self.model}")
    
    def connect(self, conn: SnowflakeConnection):
        """
        Set the Snowflake connection to use for Cortex LLM calls.
        
        Args:
            conn: Snowflake connection object
        """
        self._conn = conn
        logger.info("Connected Cortex LLM client to Snowflake")
    
    def generate_description(self, context: str, prompt: str) -> str:
        """
        Generate a description using Snowflake Cortex.
        
        Args:
            context (str): Context information to include in the prompt
            prompt (str): The prompt template to use
            
        Returns:
            str: The generated description
        """
        if not self._conn:
            logger.error("No Snowflake connection available for Cortex LLM")
            return "Error: No Snowflake connection (call connect() first)"
        
        full_prompt = f"{prompt}\n\nContext:\n{context}"
        # Escape single quotes in the prompt to prevent SQL injection
        safe_prompt = full_prompt.replace("'", "''")
        
        try:
            # Limit the prompt size to avoid Snowflake query size limits
            if len(safe_prompt) > 10000:
                logger.warning(f"Trimming prompt from {len(safe_prompt)} to 10000 characters")
                safe_prompt = safe_prompt[:10000]
            
            # Call Snowflake Cortex COMPLETE function via SQL with statement timeout
            # Adding statement_timeout_in_seconds to prevent query from hanging
            self._conn.cursor().execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 60")
            
            complete_sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{self.model}', '{safe_prompt}')"
            cursor = self._conn.cursor()
            cursor.execute(complete_sql)
            result = cursor.fetchone()
            
            # Reset the timeout to default
            self._conn.cursor().execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 0")
            
            if result and len(result) > 0:
                return str(result[0]).strip()
            else:
                logger.warning("Empty result from Cortex LLM")
                return "No response from Cortex LLM"
        except Exception as e:
            logger.error(f"Error generating description with Cortex LLM: {e}")
            # Try to reset the timeout even after an error
            try:
                self._conn.cursor().execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 0")
            except:
                pass
                
            if hasattr(self, 'fallback_client') and self.fallback_client:
                logger.info("Falling back to alternative LLM provider")
                return self.fallback_client.generate_description(context, prompt)
            return f"Error generating description: {str(e)}"


class OpenAILLMClient(LLMClient):
    """Client for OpenAI models."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the OpenAI LLM client.
        
        Args:
            config: LLM configuration
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The openai package is required to use OpenAI models. "
                "Install it with 'pip install openai'."
            )
        
        self.model = config.model
        self.api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided in config or as OPENAI_API_KEY environment variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens or 500
        
        logger.info(f"Initialized OpenAI client with model: {self.model}")
    
    def generate_description(self, context: str, prompt: str) -> str:
        """
        Generate a description using OpenAI.
        
        Args:
            context (str): Context information to include in the prompt
            prompt (str): The prompt template to use
            
        Returns:
            str: The generated description
        """
        full_prompt = f"{prompt}\n\nContext:\n{context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for generating semantic model descriptions."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating description with OpenAI: {e}")
            if hasattr(self, 'fallback_client') and self.fallback_client:
                logger.info("Falling back to alternative LLM provider")
                return self.fallback_client.generate_description(context, prompt)
            return "Auto-generated description (error occurred)"


class AzureOpenAILLMClient(LLMClient):
    """Client for Azure OpenAI models."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the Azure OpenAI LLM client.
        
        Args:
            config: LLM configuration
        """
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The openai package is required to use Azure OpenAI models. "
                "Install it with 'pip install openai'."
            )
        
        self.model = config.model
        self.api_key = config.api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Azure OpenAI API key must be provided in config or as AZURE_OPENAI_API_KEY environment variable")
        
        self.api_endpoint = config.api_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.api_endpoint:
            raise ValueError("Azure OpenAI endpoint must be provided in config or as AZURE_OPENAI_ENDPOINT environment variable")
        
        self.api_version = config.api_version or "2023-05-15"
        self.deployment_name = config.azure_deployment_name
        if not self.deployment_name:
            raise ValueError("Azure OpenAI deployment name must be provided in config")
        
        self.client = openai.AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.api_endpoint,
            api_version=self.api_version
        )
        
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens or 500
        
        logger.info(f"Initialized Azure OpenAI client with deployment: {self.deployment_name}")
    
    def generate_description(self, context: str, prompt: str) -> str:
        """
        Generate a description using Azure OpenAI.
        
        Args:
            context (str): Context information to include in the prompt
            prompt (str): The prompt template to use
            
        Returns:
            str: The generated description
        """
        full_prompt = f"{prompt}\n\nContext:\n{context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for generating semantic model descriptions."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating description with Azure OpenAI: {e}")
            if hasattr(self, 'fallback_client') and self.fallback_client:
                logger.info("Falling back to alternative LLM provider")
                return self.fallback_client.generate_description(context, prompt)
            return "Auto-generated description (error occurred)"


class AnthropicLLMClient(LLMClient):
    """Client for Anthropic models."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the Anthropic LLM client.
        
        Args:
            config: LLM configuration
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "The anthropic package is required to use Anthropic models. "
                "Install it with 'pip install anthropic'."
            )
        
        self.model = config.model
        self.api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided in config or as ANTHROPIC_API_KEY environment variable")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens or 500
        
        logger.info(f"Initialized Anthropic client with model: {self.model}")
    
    def generate_description(self, context: str, prompt: str) -> str:
        """
        Generate a description using Anthropic.
        
        Args:
            context (str): Context information to include in the prompt
            prompt (str): The prompt template to use
            
        Returns:
            str: The generated description
        """
        full_prompt = f"{prompt}\n\nContext:\n{context}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                system="You are a helpful assistant for generating semantic model descriptions.",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error generating description with Anthropic: {e}")
            if hasattr(self, 'fallback_client') and self.fallback_client:
                logger.info("Falling back to alternative LLM provider")
                return self.fallback_client.generate_description(context, prompt)
            return "Auto-generated description (error occurred)"


def get_llm_client(config: LLMConfig) -> LLMClient:
    """
    Factory function to create the appropriate LLM client based on configuration.
    
    Args:
        config: LLM configuration
        
    Returns:
        An LLM client instance
    """
    # Map provider to client class
    provider_map = {
        "cortex": CortexLLMClient,
        "openai": OpenAILLMClient,
        "azure_openai": AzureOpenAILLMClient,
        "anthropic": AnthropicLLMClient,
    }
    
    if config.provider not in provider_map:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
    
    # Create the primary client
    client_class = provider_map[config.provider]
    client = client_class(config)
    
    # Set up fallback if configured
    if config.fallback_provider and config.fallback_provider != config.provider:
        if config.fallback_provider not in provider_map:
            logger.warning(f"Unsupported fallback LLM provider: {config.fallback_provider}")
        else:
            # Create a modified config for the fallback
            fallback_config = LLMConfig(
                provider=config.fallback_provider,
                model=config.fallback_model or config.model,
                api_key=config.fallback_api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            # Create fallback client
            fallback_client_class = provider_map[config.fallback_provider]
            client.fallback_client = fallback_client_class(fallback_config)
            
    return client 
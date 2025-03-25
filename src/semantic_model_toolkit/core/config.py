"""Configuration handling for semantic model generator."""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Literal

import yaml


@dataclass
class SnowflakeConfig:
    """Snowflake connection configuration."""
    
    account: str
    user: str
    password: Optional[str] = None
    role: Optional[str] = None
    warehouse: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    private_key_path: Optional[str] = None
    private_key_passphrase: Optional[str] = None
    token: Optional[str] = None
    authenticator: Optional[str] = None


@dataclass
class SemanticModelConfig:
    """Semantic model configuration."""
    
    name: str
    base_tables: List[str]
    n_sample_values: int = 3
    allow_joins: bool = False


@dataclass
class LLMConfig:
    """LLM configuration for description generation."""
    
    provider: Literal["cortex", "openai", "azure_openai", "anthropic"] = "cortex"
    model: str = "llama3-8b"
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    azure_deployment_name: Optional[str] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    fallback_provider: Optional[str] = None
    fallback_api_key: Optional[str] = None
    fallback_model: Optional[str] = None


@dataclass
class Config:
    """Main configuration class for semantic model generator."""
    
    snowflake: SnowflakeConfig
    semantic_model: SemanticModelConfig
    llm: Optional[LLMConfig] = None


def load_config(config_path: str) -> Config:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file (JSON or YAML)
        
    Returns:
        Config object
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Determine file type by extension
    _, ext = os.path.splitext(config_path)
    
    with open(config_path, "r") as f:
        if ext.lower() in [".yaml", ".yml"]:
            config_dict = yaml.safe_load(f)
        elif ext.lower() == ".json":
            config_dict = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {ext}")
    
    return parse_config_dict(config_dict)


def parse_config_dict(config_dict: Dict) -> Config:
    """
    Parse a configuration dictionary into a Config object.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Config object
    """
    snowflake_config = SnowflakeConfig(**config_dict["snowflake"])
    semantic_model_config = SemanticModelConfig(**config_dict["semantic_model"])
    
    llm_config = None
    if "llm" in config_dict:
        # Convert from legacy format if needed
        if "use_cortex" in config_dict["llm"] and "provider" not in config_dict["llm"]:
            if config_dict["llm"]["use_cortex"]:
                config_dict["llm"]["provider"] = "cortex"
            elif "fallback_service" in config_dict["llm"]:
                config_dict["llm"]["provider"] = config_dict["llm"].get("fallback_service", "openai")
                config_dict["llm"]["api_key"] = config_dict["llm"].get("fallback_api_key")
            
            # Remove legacy fields to avoid conflicts
            config_dict["llm"].pop("use_cortex", None)
            config_dict["llm"].pop("fallback_service", None)
            config_dict["llm"].pop("fallback_api_key", None)
            
        llm_config = LLMConfig(**config_dict["llm"])
    
    return Config(
        snowflake=snowflake_config,
        semantic_model=semantic_model_config,
        llm=llm_config,
    )


def config_from_dict(config_dict: Dict) -> Config:
    """
    Create a Config object from a dictionary.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Config object
    """
    return parse_config_dict(config_dict)


def config_to_dict(config: Config) -> Dict:
    """
    Convert a Config object to a dictionary.
    
    Args:
        config: Config object
        
    Returns:
        Configuration dictionary
    """
    result = {
        "snowflake": {
            "account": config.snowflake.account,
            "user": config.snowflake.user,
        },
        "semantic_model": {
            "name": config.semantic_model.name,
            "base_tables": config.semantic_model.base_tables,
            "n_sample_values": config.semantic_model.n_sample_values,
            "allow_joins": config.semantic_model.allow_joins,
        }
    }
    
    # Add optional Snowflake parameters
    for attr in ["password", "role", "warehouse", "database", "schema", 
                 "private_key_path", "private_key_passphrase", "token", "authenticator"]:
        if getattr(config.snowflake, attr) is not None:
            result["snowflake"][attr] = getattr(config.snowflake, attr)
    
    # Add LLM config if present
    if config.llm is not None:
        result["llm"] = {
            "provider": config.llm.provider,
            "model": config.llm.model,
        }
        
        # Add optional LLM parameters
        for attr in ["api_key", "api_endpoint", "api_version", "azure_deployment_name", 
                    "temperature", "max_tokens", "fallback_provider", "fallback_api_key", 
                    "fallback_model"]:
            if getattr(config.llm, attr) is not None:
                result["llm"][attr] = getattr(config.llm, attr)
    
    return result 
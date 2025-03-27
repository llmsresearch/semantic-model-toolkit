"""Main entry point for semantic model generation."""

from typing import Dict, Optional, Union

from loguru import logger
from snowflake.connector import SnowflakeConnection

from semantic_model_toolkit.core.config import Config, config_from_dict, load_config
from semantic_model_toolkit.data_processing import proto_utils
from semantic_model_toolkit.protos import semantic_model_pb2
from semantic_model_toolkit.snowflake_utils.utils import create_snowflake_connection
from semantic_model_toolkit.generate_model import (
    generate_model_str_from_snowflake,
    raw_schema_to_semantic_context,
)


def generate_semantic_model(
    config: Union[Dict, Config],
    snowflake_connection: Optional[SnowflakeConnection] = None,
) -> str:
    """
    Generate a semantic model YAML string based on provided configuration.
    
    Args:
        config: Configuration dictionary or Config object containing:
            - snowflake: Snowflake connection parameters (if connection not provided)
                - account: Snowflake account
                - user: Snowflake username
                - password/private_key/token: Authentication methods
                - role, warehouse, etc: Optional connection parameters
            - semantic_model: Semantic model configuration
                - name: Name for the semantic model
                - base_tables: List of fully qualified table names
                - n_sample_values: Number of sample values to include
                - allow_joins: Whether to include placeholder joins
            - llm: Configuration for LLM description generation (optional)
                - provider: LLM provider to use (cortex, openai, azure_openai, anthropic)
                - model: Model name to use
                - api_key: API key for the LLM service
                - Other provider-specific parameters
        snowflake_connection: Optional pre-established Snowflake connection
        
    Returns:
        The generated semantic model as a YAML string
    """
    # Convert dict to Config object if needed
    if isinstance(config, dict):
        config = config_from_dict(config)
    
    # Create Snowflake connection if not provided
    if not snowflake_connection:
        snowflake_connection = create_snowflake_connection(
            account=config.snowflake.account,
            user=config.snowflake.user,
            password=config.snowflake.password,
            role=config.snowflake.role,
            warehouse=config.snowflake.warehouse,
            database=config.snowflake.database,
            schema=config.snowflake.schema,
            private_key_path=config.snowflake.private_key_path,
            private_key_passphrase=config.snowflake.private_key_passphrase,
            token=config.snowflake.token,
            authenticator=config.snowflake.authenticator,
        )
    
    try:
        # Generate YAML directly from Snowflake
        yaml_str = generate_model_str_from_snowflake(
            base_tables=config.semantic_model.base_tables,
            semantic_model_name=config.semantic_model.name,
            conn=snowflake_connection,
            n_sample_values=config.semantic_model.n_sample_values,
            allow_joins=config.semantic_model.allow_joins,
            llm_config=config.llm,
        )
        
        return yaml_str
    
    finally:
        # Close connection if we created it
        if snowflake_connection and not hasattr(snowflake_connection, '_is_closed'):
            try:
                snowflake_connection.close()
            except:
                pass


def generate_from_file(config_path: str) -> str:
    """
    Generate a semantic model YAML string based on a configuration file.
    
    Args:
        config_path: Path to the configuration file (YAML or JSON)
        
    Returns:
        The generated semantic model as a YAML string
    """
    config = load_config(config_path)
    return generate_semantic_model(config)


def load_semantic_model_from_string(yaml_str: str) -> semantic_model_pb2.SemanticModel:
    """
    Load a semantic model from a YAML string.
    
    Args:
        yaml_str: YAML string representation of the semantic model
        
    Returns:
        Semantic model as a protobuf object
    """
    return proto_utils.yaml_to_semantic_model(yaml_str)


def load_semantic_model_from_file(file_path: str) -> semantic_model_pb2.SemanticModel:
    """
    Load a semantic model from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Semantic model as a protobuf object
    """
    with open(file_path, 'r') as f:
        yaml_str = f.read()
    
    return load_semantic_model_from_string(yaml_str) 
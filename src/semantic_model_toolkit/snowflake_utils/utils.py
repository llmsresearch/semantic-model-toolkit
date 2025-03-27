from typing import Dict, Optional, Union

from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection

from semantic_model_toolkit.data_processing.data_types import FQNParts


def create_fqn_table(fqn_str: str) -> FQNParts:
    if fqn_str.count(".") != 2:
        raise ValueError(
            "Expected to have a table fully qualified name following the {database}.{schema}.{table} format."
            + f"Instead found {fqn_str}"
        )
    database, schema, table = fqn_str.split(".")
    return FQNParts(
        database=database.upper(), schema_name=schema.upper(), table=table.upper()
    )


def create_connection_parameters(
    user: str,
    account: str,
    password: Optional[str] = None,
    host: Optional[str] = None,
    role: Optional[str] = None,
    warehouse: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    authenticator: Optional[str] = None,
    passcode: Optional[str] = None,
    passcode_in_password: Optional[bool] = None,
) -> Dict[str, Union[str, bool]]:
    connection_parameters: Dict[str, Union[str, bool]] = dict(
        user=user, account=account
    )
    if password:
        connection_parameters["password"] = password
    if role:
        connection_parameters["role"] = role
    if warehouse:
        connection_parameters["warehouse"] = warehouse
    if database:
        connection_parameters["database"] = database
    if schema:
        connection_parameters["schema"] = schema
    if authenticator:
        connection_parameters["authenticator"] = authenticator
    if host:
        connection_parameters["host"] = host
    if passcode:
        connection_parameters["passcode"] = passcode
    if passcode_in_password:
        connection_parameters["passcode_in_password"] = passcode_in_password
    return connection_parameters


def _connection(
    connection_parameters: Dict[str, Union[str, bool]]
) -> SnowflakeConnection:
    # https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect
    return connect(**connection_parameters)


def snowflake_connection(
    user: str,
    account: str,
    role: str,
    warehouse: str,
    password: Optional[str] = None,
    host: Optional[str] = None,
    authenticator: Optional[str] = None,
    passcode: Optional[str] = None,
    passcode_in_password: Optional[bool] = None,
) -> SnowflakeConnection:
    """
    Returns a Snowflake Connection to the specified account.
    """
    return _connection(
        create_connection_parameters(
            user=user,
            password=password,
            host=host,
            account=account,
            role=role,
            warehouse=warehouse,
            authenticator=authenticator,
            passcode=passcode,
            passcode_in_password=passcode_in_password,
        )
    )


def create_snowflake_connection(
    account: str,
    user: str,
    password: Optional[str] = None,
    role: Optional[str] = None,
    warehouse: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    host: Optional[str] = None,
    private_key_path: Optional[str] = None,
    private_key_passphrase: Optional[str] = None,
    token: Optional[str] = None,
    authenticator: Optional[str] = None,
) -> SnowflakeConnection:
    """
    Creates a Snowflake connection with the provided parameters.
    
    This function supports multiple authentication methods:
    1. Username/password
    2. Key pair authentication
    3. OAuth token
    4. External browser/SSO (via authenticator)
    
    Args:
        account: Snowflake account identifier
        user: Snowflake username
        password: Password for password authentication
        role: Role to use for the connection
        warehouse: Warehouse to use
        database: Default database
        schema: Default schema
        host: Host URL override (optional)
        private_key_path: Path to private key file for key pair authentication
        private_key_passphrase: Passphrase for the private key
        token: OAuth token for token-based authentication
        authenticator: Authenticator for external browser/SSO auth
        
    Returns:
        A Snowflake connection
    """
    connection_params = {
        "user": user,
        "account": account,
    }
    
    # Add optional parameters
    if password:
        connection_params["password"] = password
    if role:
        connection_params["role"] = role
    if warehouse:
        connection_params["warehouse"] = warehouse
    if database:
        connection_params["database"] = database
    if schema:
        connection_params["schema"] = schema
    if host:
        connection_params["host"] = host
    if authenticator:
        connection_params["authenticator"] = authenticator
        
    # Key pair authentication
    if private_key_path:
        import os
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        
        with open(os.path.expanduser(private_key_path), "rb") as key:
            p_key = load_pem_private_key(
                key.read(),
                password=private_key_passphrase.encode() if private_key_passphrase else None,
                backend=default_backend()
            )
            
        connection_params["private_key"] = p_key
        
    # OAuth token
    if token:
        connection_params["token"] = token
        
    return connect(**connection_params)

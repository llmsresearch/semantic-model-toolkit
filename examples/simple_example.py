"""Simple example showing basic usage of the semantic model toolkit."""

import os
from semantic_model_toolkit import generate_semantic_model, generate_from_file

def main():
    """
    Demonstrates two ways to use the semantic model toolkit:
    1. With a dictionary config
    2. With a config file
    """
    # # Method 1: Using a dictionary configuration with Snowflake Cortex
    # config = {
    #     "snowflake": {
    #         "account": "your_account",
    #         "user": "your_username",
    #         "password": "your_password",
    #         "role": "your_role",
    #         "warehouse": "your_warehouse",
    #     },
    #     "semantic_model": {
    #         "name": "sales_analytics",
    #         "base_tables": ["YOUR_DB.YOUR_SCHEMA.YOUR_TABLE"],
    #         "n_sample_values": 3,
    #         "allow_joins": False,
    #     },
    #     "llm": {
    #         "provider": "cortex",
    #         "model": "llama3-8b",
    #     }
    # }
    
    # print("Method 1: Using dictionary configuration with Cortex")
    # print("---------------------------------------------------")
    # try:
    #     yaml_str = generate_semantic_model(config)
        
    #     # Here the user can save the yaml_str to a file
    #     print("Generated semantic model YAML:")
    #     print("-----------------------------")
    #     print(yaml_str[:300] + "...\n")  # Print first 300 chars as preview
        
    #     # Example of how to save the YAML to a file
    #     print("Example of how to save the YAML to a file:")
    #     print("with open('my_semantic_model.yaml', 'w') as f:")
    #     print("    f.write(yaml_str)")
        
    # except Exception as e:
    #     print(f"Error generating model with dictionary config: {e}")
    
    # Method 2: Using a configuration file
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    print("\nMethod 2: Using configuration file")
    print("----------------------------------")
    try:
        yaml_str = generate_from_file(config_path)
        print("Generated semantic model YAML from config file (preview):")
        print(yaml_str[:600] + "...\n")  # Print first 300 chars as preview
        with open('my_semantic_model.yaml', 'w') as f:
            f.write(yaml_str)
    except Exception as e:
        print(f"Error generating model from config file: {e}")

    # # Method 3: Using OpenAI for descriptions
    # print("\nMethod 3: Using OpenAI for descriptions")
    # print("--------------------------------------")
    # # Set your OpenAI API key in the environment or in the config:
    # # os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    # # Create a config using OpenAI
    # openai_config = {
    #     "snowflake": {
    #         "account": "your_account",
    #         "user": "your_username",
    #         "password": "your_password",
    #     },
    #     "semantic_model": {
    #         "name": "sales_analytics_openai",
    #         "base_tables": ["YOUR_DB.YOUR_SCHEMA.YOUR_TABLE"],
    #         "n_sample_values": 3,
    #     },
    #     "llm": {
    #         "provider": "openai",
    #         "model": "gpt-4",
    #         "api_key": "your_openai_api_key",  # Set your API key here or in env vars
    #         "temperature": 0.2,
    #         "max_tokens": 500
    #     }
    # }
    
    # print("Configuration with OpenAI (API key would be needed to run):")
    # print("yaml_str = generate_semantic_model(openai_config)")
    
    # # Method 4: Using Azure OpenAI for descriptions
    # print("\nMethod 4: Using Azure OpenAI for descriptions")
    # print("--------------------------------------------")
    # azure_config = {
    #     "snowflake": {
    #         "account": "your_account",
    #         "user": "your_username",
    #         "password": "your_password",
    #     },
    #     "semantic_model": {
    #         "name": "sales_analytics_azure",
    #         "base_tables": ["YOUR_DB.YOUR_SCHEMA.YOUR_TABLE"],
    #     },
    #     "llm": {
    #         "provider": "azure_openai",
    #         "azure_deployment_name": "your_deployment_name",
    #         "api_key": "your_azure_api_key",
    #         "api_endpoint": "https://your-resource.openai.azure.com/",
    #         "api_version": "2023-05-15"
    #     }
    # }
    
    # print("Configuration with Azure OpenAI (API details would be needed to run):")
    # print("yaml_str = generate_semantic_model(azure_config)")

    # # Method 5: Using Anthropic for descriptions
    # print("\nMethod 5: Using Anthropic for descriptions")
    # print("----------------------------------------")
    # anthropic_config = {
    #     "snowflake": {
    #         "account": "your_account",
    #         "user": "your_username",
    #         "password": "your_password",
    #     },
    #     "semantic_model": {
    #         "name": "sales_analytics_anthropic",
    #         "base_tables": ["YOUR_DB.YOUR_SCHEMA.YOUR_TABLE"],
    #     },
    #     "llm": {
    #         "provider": "anthropic",
    #         "model": "claude-3-sonnet-20240229",
    #         "api_key": "your_anthropic_api_key"
    #     }
    # }
    
    # print("Configuration with Anthropic (API key would be needed to run):")
    # print("yaml_str = generate_semantic_model(anthropic_config)")

if __name__ == "__main__":
    main() 
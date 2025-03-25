"""Tests for the config module."""

import os
import tempfile
import unittest

from semantic_model_generator.core.config import (
    Config,
    LLMConfig,
    OutputConfig,
    SemanticModelConfig,
    SnowflakeConfig,
    config_from_dict,
    config_to_dict,
)


class TestConfigModule(unittest.TestCase):
    """Tests for the config module."""

    def test_config_from_dict(self):
        """Test config_from_dict function."""
        config_dict = {
            "snowflake": {
                "account": "test_account",
                "user": "test_user",
                "password": "test_password",
            },
            "semantic_model": {
                "name": "test_model",
                "base_tables": ["DB.SCHEMA.TABLE"],
                "n_sample_values": 5,
            },
            "output": {
                "path": "./test_output",
                "filename": "test.yaml",
            },
            "llm": {
                "use_cortex": True,
                "model": "llama3-8b",
            },
        }
        
        config = config_from_dict(config_dict)
        
        # Check config is created correctly
        self.assertEqual(config.snowflake.account, "test_account")
        self.assertEqual(config.snowflake.user, "test_user")
        self.assertEqual(config.snowflake.password, "test_password")
        
        self.assertEqual(config.semantic_model.name, "test_model")
        self.assertEqual(config.semantic_model.base_tables, ["DB.SCHEMA.TABLE"])
        self.assertEqual(config.semantic_model.n_sample_values, 5)
        
        self.assertEqual(config.output.path, "./test_output")
        self.assertEqual(config.output.filename, "test.yaml")
        
        self.assertEqual(config.llm.use_cortex, True)
        self.assertEqual(config.llm.model, "llama3-8b")

    def test_config_to_dict(self):
        """Test config_to_dict function."""
        config = Config(
            snowflake=SnowflakeConfig(
                account="test_account",
                user="test_user",
                password="test_password",
            ),
            semantic_model=SemanticModelConfig(
                name="test_model",
                base_tables=["DB.SCHEMA.TABLE"],
                n_sample_values=5,
            ),
            output=OutputConfig(
                path="./test_output",
                filename="test.yaml",
            ),
            llm=LLMConfig(
                use_cortex=True,
                model="llama3-8b",
            ),
        )
        
        config_dict = config_to_dict(config)
        
        # Check dictionary is created correctly
        self.assertEqual(config_dict["snowflake"]["account"], "test_account")
        self.assertEqual(config_dict["snowflake"]["user"], "test_user")
        self.assertEqual(config_dict["snowflake"]["password"], "test_password")
        
        self.assertEqual(config_dict["semantic_model"]["name"], "test_model")
        self.assertEqual(config_dict["semantic_model"]["base_tables"], ["DB.SCHEMA.TABLE"])
        self.assertEqual(config_dict["semantic_model"]["n_sample_values"], 5)
        
        self.assertEqual(config_dict["output"]["path"], "./test_output")
        self.assertEqual(config_dict["output"]["filename"], "test.yaml")
        
        self.assertEqual(config_dict["llm"]["use_cortex"], True)
        self.assertEqual(config_dict["llm"]["model"], "llama3-8b")


if __name__ == "__main__":
    unittest.main() 
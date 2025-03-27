"""Tests for the core module."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from semantic_model_toolkit.core.config import Config, OutputConfig, SemanticModelConfig, SnowflakeConfig
from semantic_model_toolkit.core.model_generator import generate_semantic_model, save_semantic_model


class TestCoreModule(unittest.TestCase):
    """Tests for the core module."""

    def test_save_semantic_model(self):
        """Test save_semantic_model function."""
        yaml_str = "name: test\ndescription: test description"
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = save_semantic_model(yaml_str, temp_dir, "test.yaml")
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, "r") as f:
                content = f.read()
                self.assertEqual(content, yaml_str)

    @patch("semantic_model_toolkit.core.model_generator.raw_schema_to_semantic_context")
    @patch("semantic_model_toolkit.core.model_generator.generate_model_str_from_semantic_context")
    @patch("semantic_model_toolkit.core.model_generator.create_snowflake_connection")
    def test_generate_semantic_model(self, mock_create_conn, mock_generate_str, mock_raw_schema):
        """Test generate_semantic_model function with mocked dependencies."""
        # Setup mocks
        mock_conn = MagicMock()
        mock_create_conn.return_value = mock_conn
        mock_conn._is_closed.return_value = False
        
        mock_context = MagicMock()
        mock_raw_schema.return_value = mock_context
        
        mock_generate_str.return_value = "name: test_model\ndescription: test"
        
        # Test config
        config = Config(
            snowflake=SnowflakeConfig(
                account="test_account",
                user="test_user",
                password="test_password",
            ),
            semantic_model=SemanticModelConfig(
                name="test_model",
                base_tables=["DB.SCHEMA.TABLE"],
            ),
            output=OutputConfig(
                path="./test_output",
            ),
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call function
            yaml_str = generate_semantic_model(config, output_path=temp_dir)
            
            # Verify results
            self.assertEqual(yaml_str, "name: test_model\ndescription: test")
            mock_create_conn.assert_called_once()
            mock_raw_schema.assert_called_once_with(
                base_tables=["DB.SCHEMA.TABLE"], 
                semantic_model_name="test_model", 
                conn=mock_conn, 
                n_sample_values=3, 
                allow_joins=False
            )
            mock_generate_str.assert_called_once_with(mock_context)
            mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main() 
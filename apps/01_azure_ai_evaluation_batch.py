#!/usr/bin/env python3
"""
Azure AI Evaluation Batch Processing Script

This script performs batch evaluation of generative AI applications using Azure AI Evaluation SDK.
Designed for CI/CD execution with environment variable configuration.

Required Environment Variables:
    AZURE_AI_PROJECT_ENDPOINT: Azure AI Foundry project endpoint
    AZURE_OPENAI_ENDPOINT: Azure OpenAI service endpoint
    AZURE_OPENAI_API_KEY: Azure OpenAI API key (prefer managed identity in production)
    AZURE_OPENAI_CHAT_DEPLOYMENT: Chat completion deployment name
    AZURE_OPENAI_API_VERSION: Azure OpenAI API version
    EVAL_DATA_PATH: Path to evaluation data file (default: ../data/eval_data.jsonl)
    OUTPUT_PATH: Path for evaluation results (optional)

Usage:
    python 01_azure_ai_evaluation_batch.py
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

# Third-party imports
from dotenv import load_dotenv
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.evaluation import (
    evaluate,
    RetrievalEvaluator,
    QAEvaluator,
    ContentSafetyEvaluator,
    ResponseCompletenessEvaluator,
    HateUnfairnessEvaluator
)

# Load environment variables from .env file
load_dotenv()

def configure_logging():
    """Configure logging based on environment variables"""
    # Get log level from environment variable (default: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Set the main logging level
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure basic logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('evaluation.log')
        ],
        force=True  # Override any existing configuration
    )
    
    # Suppress verbose logging from Azure SDKs and HTTP libraries unless in debug mode
    if not debug_mode:
        logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
        logging.getLogger('azure.identity').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('azure.core').setLevel(logging.WARNING)
    else:
        # In debug mode, show more details but still suppress the most verbose ones
        logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.INFO)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    
    # Keep important Azure AI evaluation logs at INFO level
    logging.getLogger('azure.ai.evaluation').setLevel(logging.INFO)
    logging.getLogger('azure.ai.projects').setLevel(logging.INFO)
    logging.getLogger('promptflow').setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

# Configure logging and get logger
logger = configure_logging()

class AzureAIEvaluationConfig:
    """Configuration class for Azure AI Evaluation"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        self.azure_ai_project_endpoint = self._get_required_env("AZURE_AI_PROJECT_ENDPOINT")
        self.azure_openai_endpoint = self._get_required_env("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_key = self._get_required_env("AZURE_OPENAI_API_KEY")
        self.azure_openai_chat_deployment = self._get_required_env("AZURE_OPENAI_CHAT_DEPLOYMENT")
        self.azure_openai_api_version = self._get_required_env("AZURE_OPENAI_API_VERSION")
        
        # Optional configurations
        self.eval_data_path = os.getenv("EVAL_DATA_PATH", "../data/eval_data.jsonl")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.threshold = int(os.getenv("EVALUATION_THRESHOLD", "3"))
        
        logger.info("Configuration loaded successfully")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @property
    def model_config(self) -> Dict[str, str]:
        """Get OpenAI model configuration"""
        return {
            "azure_endpoint": self.azure_openai_endpoint,
            "api_key": self.azure_openai_api_key,
            "azure_deployment": self.azure_openai_chat_deployment,
            "api_version": self.azure_openai_api_version,
        }


class AzureAIEvaluator:
    """Azure AI Evaluation batch processor"""
    
    def __init__(self, config: AzureAIEvaluationConfig):
        """Initialize evaluator with configuration"""
        self.config = config
        self.credential = DefaultAzureCredential()
        self.project_client = None
        self.evaluators = {}
        
        logger.info("Initializing Azure AI Evaluator")
        self._setup_azure_ai_project()
        self._setup_evaluators()
    
    def _setup_azure_ai_project(self) -> None:
        """Setup Azure AI project client with managed identity"""
        try:
            self.project_client = AIProjectClient(
                credential=self.credential,
                endpoint=self.config.azure_ai_project_endpoint,
            )
            logger.info("Azure AI Project client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Project client: {e}")
            raise
    
    def _setup_evaluators(self) -> None:
        """Initialize all evaluators"""
        try:
            # RAG Evaluators
            self.evaluators["retrieval"] = RetrievalEvaluator(
                model_config=self.config.model_config,
                threshold=self.config.threshold
            )
            
            self.evaluators["response_completeness"] = ResponseCompletenessEvaluator(
                model_config=self.config.model_config,
                threshold=self.config.threshold
            )
            
            # General Purpose Evaluators
            self.evaluators["qa"] = QAEvaluator(
                model_config=self.config.model_config,
                threshold=self.config.threshold
            )
            
            # Safety Evaluators (using managed identity)
            self.evaluators["content_safety"] = ContentSafetyEvaluator(
                credential=self.credential,
                azure_ai_project=self.config.azure_ai_project_endpoint
            )
            
            self.evaluators["hate_unfairness"] = HateUnfairnessEvaluator(
                credential=self.credential,
                azure_ai_project=self.config.azure_ai_project_endpoint,
                threshold=self.config.threshold
            )
            
            logger.info(f"Initialized {len(self.evaluators)} evaluators successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize evaluators: {e}")
            raise
    
    def load_evaluation_data(self) -> pd.DataFrame:
        """Load evaluation data from file"""
        try:
            data_path = Path(self.config.eval_data_path)
            if not data_path.exists():
                raise FileNotFoundError(f"Evaluation data file not found: {data_path}")
            
            if data_path.suffix == '.jsonl':
                df = pd.read_json(data_path, lines=True)
            elif data_path.suffix == '.json':
                df = pd.read_json(data_path)
            else:
                raise ValueError(f"Unsupported file format: {data_path.suffix}")
            
            logger.info(f"Loaded {len(df)} evaluation records from {data_path}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load evaluation data: {e}")
            raise
    
    def validate_data_schema(self, df: pd.DataFrame) -> bool:
        """Validate that the data has required columns"""
        required_columns = ["query", "retrieved_results", "response", "ground_truth"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        logger.info("Data schema validation passed")
        return True
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run batch evaluation on the dataset"""
        try:
            # Load and validate data
            df = self.load_evaluation_data()
            if not self.validate_data_schema(df):
                raise ValueError("Data schema validation failed")
            
            # Ensure output directory exists if output_path is specified
            if self.config.output_path:
                output_path = Path(self.config.output_path)
                
                # If output_path is a file path, create its parent directory
                if output_path.suffix:
                    output_dir = output_path.parent
                else:
                    # If output_path is a directory path, create the directory itself
                    output_dir = output_path
                
                output_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured output directory exists: {output_dir}")
                
                # Also check if the Azure AI SDK expects a directory instead of a file
                # Some versions may expect the parent directory to exist
                if output_path.suffix:
                    # For file paths, also ensure the directory exists
                    actual_output_dir = output_path.parent
                    if not actual_output_dir.exists():
                        actual_output_dir.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created output directory: {actual_output_dir}")
            
            logger.info("Starting batch evaluation...")
            
            # Select evaluators for batch evaluation
            selected_evaluators = {
                "retrieval": self.evaluators["retrieval"],
                "qa": self.evaluators["qa"],
                "content_safety": self.evaluators["content_safety"],
            }
            
            # Configure column mapping
            evaluator_config = {
                "default": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "context": "${data.retrieved_results}",
                        "response": "${data.response}",
                        "ground_truth": "${data.ground_truth}"
                    }
                }
            }
            
            # Run evaluation
            result = evaluate(
                data=self.config.eval_data_path,
                evaluators=selected_evaluators,
                evaluator_config=evaluator_config,
                azure_ai_project=self.config.azure_ai_project_endpoint,
                output_path=self.config.output_path
            )
            
            logger.info("Batch evaluation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def save_results(self, result: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """Save evaluation results to file"""
        try:
            if output_path is None:
                output_path = self.config.output_path or "evaluation_results.json"
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert result to JSON serializable format
            serializable_result = self._make_serializable(result)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON serializable format"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)
    
    def print_summary(self, result: Dict[str, Any]) -> None:
        """Print evaluation summary"""
        try:
            print("\n" + "="*50)
            print("EVALUATION SUMMARY")
            print("="*50)
            
            if 'metrics' in result:
                print("\nMetrics:")
                for metric_name, metric_value in result['metrics'].items():
                    if isinstance(metric_value, (int, float)):
                        print(f"  {metric_name}: {metric_value:.4f}")
                    else:
                        print(f"  {metric_name}: {metric_value}")
            
            if 'rows' in result:
                print(f"\nEvaluated {len(result['rows'])} rows")
            
            # Output Azure AI Foundry studio URL for GitHub Actions to pick up
            if 'studio_url' in result:
                studio_url = result['studio_url']
                print(f"\nAzure AI Foundry Results: {studio_url}")
                
                # Encode the URL to avoid GitHub Actions masking sensitive parts
                import urllib.parse
                encoded_url = urllib.parse.quote(studio_url, safe=':/?#[]@!$&\'()*+,;=')
                
                # Special format for GitHub Actions to parse (use encoded URL)
                print(f"GITHUB_ACTIONS_STUDIO_URL_ENCODED={encoded_url}")
                # Also provide the original URL in a different format
                print(f"AZURE_AI_STUDIO_LINK={studio_url}")
            
            print("\n" + "="*50)
            
        except Exception as e:
            logger.warning(f"Failed to print summary: {e}")


def main():
    """Main execution function"""
    try:
        logger.info("Starting Azure AI Evaluation batch processing")
        
        # Load configuration
        config = AzureAIEvaluationConfig()
        
        # Initialize evaluator
        evaluator = AzureAIEvaluator(config)
        
        # Run evaluation
        result = evaluator.run_evaluation()
        
        # Save results if output path is specified
        if config.output_path:
            evaluator.save_results(result)
        
        # Print summary
        evaluator.print_summary(result)
        
        logger.info("Batch evaluation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
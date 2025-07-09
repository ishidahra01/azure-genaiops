# Azure GenAI Operations

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-AI%20Services-0078d4.svg)](https://azure.microsoft.com/en-us/products/ai-services/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A collection of implementation samples and code examples for developing generative AI applications on Azure. This repository provides practical examples and reference implementations for various AI features including simple agents, evaluation frameworks, tracing, and responsible AI practices.

## 🚀 Sample Implementation Features

### AI Agent Development Samples

- **Simple Agents**: Sample implementations using Responses API
- **Semantic Kernel Integration**: Example code for AI orchestration capabilities
- **Tool Calling**: Function calling and tool integration examples
- **Model Context Protocol (MCP)**: Communication pattern samples with AI models

### Evaluation & Testing Examples

- **Batch Evaluation**: Sample code for automated evaluation using Azure AI Evaluation SDK
- **RAG Evaluation**: Reference implementation for Retrieval Augmented Generation assessment
- **Quality Metrics**: Example evaluation scripts for relevance, coherence, and safety
- **Custom Evaluators**: Sample implementations for custom evaluation criteria

### Operations & Monitoring Samples

- **Tracing**: Sample code for observability and performance monitoring
- **AI Red Teaming**: Example implementations for security testing and adversarial evaluation
- **CI/CD Integration**: GitHub Actions workflow examples for automated testing and deployment
- **Responsible AI**: Sample implementations for safety and ethical AI practices

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)
- [Support](#support)

## 🔧 Installation

### Prerequisites

- Python 3.12 or higher
- Azure subscription with AI services enabled
- Azure OpenAI service deployment

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/hishida/azure-genaiops.git
   cd azure-genaiops
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## ⚡ Quick Start

### Setting Up Environment Variables

Create a `.env` file in the project root, copy `.env.example` and add the following values:

```bash
# Azure AI Configuration
AZURE_AI_PROJECT_ENDPOINT=your_azure_ai_endpoint
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_CHAT_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

# Evaluation Configuration
EVAL_DATA_PATH=./data/eval_data.jsonl
OUTPUT_PATH=./results
LOG_LEVEL=INFO
```

### Command Line Usage

```bash
# Run batch evaluation
cd apps
python 01_azure_ai_evaluation_batch.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AZURE_AI_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | Yes | - |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Yes | - |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes | - |
| `AZURE_OPENAI_CHAT_DEPLOYMENT` | Chat completion deployment name | Yes | - |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | Yes | `2025-04-01-preview` |
| `EVAL_DATA_PATH` | Path to evaluation data file | No | `../data/eval_data.jsonl` |
| `OUTPUT_PATH` | Path for evaluation results | No | `../results/evaluation_results.json` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `DEBUG_MODE` | Enable debug mode | No | `false` |

### Evaluation Data Format

Your evaluation data should be in JSONL format:

```json
{
  "query": "What is the purpose of the AI policy interim discussion points?",
  "context": "This interim discussion points...",
  "ground_truth": "The AI policy interim discussion points were created...",
  "response": "Generated response from your AI system"
}
```

## 📖 Usage

### Sample Evaluation Script

The `01_azure_ai_evaluation_batch.py` script provides a comprehensive example of evaluation capabilities:

```python
from azure.ai.evaluation import (
    evaluate,
    RetrievalEvaluator,
    QAEvaluator,
    ContentSafetyEvaluator
)

# Configure evaluators
evaluators = {
    "retrieval": RetrievalEvaluator(),
    "qa": QAEvaluator(),
    "safety": ContentSafetyEvaluator()
}

# Run evaluation
results = evaluate(
    data=evaluation_data,
    evaluators=evaluators,
    target=your_ai_function
)
```

### Interactive Examples

Explore the Jupyter notebook `apps/01_azure_ai_evaluation.ipynb` for interactive examples and detailed walkthroughs of various AI evaluation techniques.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation

- [Azure AI Evaluation Documentation](docs/azure_ai_evaluation_batch_processing.md)
- [Federated Credentials Setup](docs/setup-federated-credentials.md)

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/hishida/azure-genaiops/issues)
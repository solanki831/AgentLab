"""
Helper functions for using AgentFactory with Ollama
All values are configurable - no hardcoded defaults
"""
import os
from typing import Optional, Dict, Tuple, List
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import ModelInfo


# ============================================================================
# DEFAULT CONFIGURATION (can be overridden via environment or parameters)
# ============================================================================

DEFAULT_CONFIG = {
    "OLLAMA_HOST": os.environ.get("OLLAMA_HOST", "localhost"),
    "OLLAMA_PORT": os.environ.get("OLLAMA_PORT", "11434"),
    "OLLAMA_MODEL": os.environ.get("OLLAMA_MODEL", "llama3.2:latest"),
    "OLLAMA_TIMEOUT": int(os.environ.get("OLLAMA_TIMEOUT", "120")),
    "OLLAMA_API_KEY": os.environ.get("OLLAMA_API_KEY", "ollama"),
}


def get_ollama_base_url(host: str = None, port: str = None) -> str:
    """
    Build Ollama base URL from host and port.
    
    Args:
        host: Ollama host (default: from env or localhost)
        port: Ollama port (default: from env or 11434)
    
    Returns:
        Full base URL string
    """
    host = host or DEFAULT_CONFIG["OLLAMA_HOST"]
    port = port or DEFAULT_CONFIG["OLLAMA_PORT"]
    return f"http://{host}:{port}/v1"


def create_ollama_client(
    model: str = None,
    base_url: str = None,
    host: str = None,
    port: str = None,
    api_key: str = None,
    vision: bool = False,
    function_calling: bool = True,
    json_output: bool = True,
    timeout: int = None
) -> OpenAIChatCompletionClient:
    """
    Create an Ollama client compatible with AgentFactory.
    
    Args:
        model: Ollama model name (e.g., "llama3.2:latest", "qwen2.5:latest")
        base_url: Full Ollama API endpoint (overrides host/port)
        host: Ollama host (default: from env OLLAMA_HOST or localhost)
        port: Ollama port (default: from env OLLAMA_PORT or 11434)
        api_key: Placeholder API key (default: from env OLLAMA_API_KEY or "ollama")
        vision: Whether model supports vision (default: False)
        function_calling: Whether model supports function calling (default: True)
        json_output: Whether model supports JSON output (default: True)
        timeout: Request timeout in seconds (default: from env OLLAMA_TIMEOUT or 120)
    
    Returns:
        OpenAIChatCompletionClient configured for Ollama
    
    Example:
        ```python
        from framework.ollama_helper import create_ollama_client
        from framework.agentFactory import AgentFactory
        
        # Using defaults from environment
        model_client = create_ollama_client()
        
        # Or with explicit config
        model_client = create_ollama_client(
            model="llama3.2:latest",
            host="192.168.1.100",
            port="11434"
        )
        
        # Use with AgentFactory
        factory = AgentFactory(model_client)
        agent = factory.create_api_contract_testing_agent()
        ```
    """
    # Resolve configuration
    model = model or DEFAULT_CONFIG["OLLAMA_MODEL"]
    api_key = api_key or DEFAULT_CONFIG["OLLAMA_API_KEY"]
    
    # Build base URL
    if base_url is None:
        base_url = get_ollama_base_url(host, port)
    
    # Create model info for Ollama models
    model_info = ModelInfo(
        vision=vision,
        function_calling=function_calling,
        json_output=json_output,
        structured_output=True,
        family="ollama"
    )
    
    return OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
        model_info=model_info
    )


def check_ollama_status(
    host: str = None,
    port: str = None,
    timeout: int = 2
) -> Tuple[bool, List[str]]:
    """
    Check if Ollama is running and list available models.
    
    Args:
        host: Ollama host (default: from env OLLAMA_HOST or localhost)
        port: Ollama port (default: from env OLLAMA_PORT or 11434)
        timeout: Connection timeout in seconds (default: 2)
    
    Returns:
        tuple: (is_running: bool, models: list)
    
    Example:
        ```python
        from framework.ollama_helper import check_ollama_status
        
        # Check default server
        is_running, models = check_ollama_status()
        
        # Check remote server
        is_running, models = check_ollama_status(host="192.168.1.100")
        
        if is_running:
            print(f"Available models: {models}")
        else:
            print("Ollama is not running")
        ```
    """
    host = host or DEFAULT_CONFIG["OLLAMA_HOST"]
    port = port or DEFAULT_CONFIG["OLLAMA_PORT"]
    url = f"http://{host}:{port}/api/tags"
    
    try:
        import requests
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return True, models
        return False, []
    except Exception:
        return False, []


def print_ollama_setup_instructions():
    """Print instructions for setting up Ollama"""
    print("\n" + "="*80)
    print(" 🦙 OLLAMA SETUP INSTRUCTIONS")
    print("="*80)
    print("\n1. Install Ollama:")
    print("   Visit: https://ollama.ai/download")
    print("   Windows: Download and run the installer")
    print()
    print("2. Start Ollama:")
    print("   Open a new terminal and run: ollama serve")
    print()
    print("3. Pull a model (choose one):")
    print("   ollama pull llama3.2:latest    # Recommended - Good balance")
    print("   ollama pull qwen2.5:latest     # Fast and efficient")
    print("   ollama pull mistral:latest     # Great performance")
    print("   ollama pull phi3:latest        # Lightweight")
    print()
    print("4. Verify installation:")
    print("   ollama list                    # Show installed models")
    print("   ollama run llama3.2           # Test the model")
    print()
    print("5. Run the demo:")
    print("   python framework\\ollama_demo.py")
    print("="*80 + "\n")


# Common Ollama models with descriptions
OLLAMA_MODELS = {
    "llama3.2:latest": {
        "name": "Llama 3.2",
        "size": "~2GB",
        "description": "Meta's latest model, good balance of performance and speed",
        "recommended": True
    },
    "qwen2.5:latest": {
        "name": "Qwen 2.5",
        "size": "~4.7GB", 
        "description": "Alibaba's model, excellent for coding and reasoning",
        "recommended": True
    },
    "mistral:latest": {
        "name": "Mistral",
        "size": "~4.1GB",
        "description": "High-performance model from Mistral AI",
        "recommended": True
    },
    "phi3:latest": {
        "name": "Phi-3",
        "size": "~2.3GB",
        "description": "Microsoft's lightweight model, fast inference",
        "recommended": False
    },
    "llama3.1:latest": {
        "name": "Llama 3.1",
        "size": "~4.7GB",
        "description": "Previous version, still very capable",
        "recommended": False
    },
    "codellama:latest": {
        "name": "Code Llama",
        "size": "~3.8GB",
        "description": "Specialized for code generation and analysis",
        "recommended": False
    }
}


def list_recommended_models():
    """Print recommended Ollama models for testing agents"""
    print("\n" + "="*80)
    print(" RECOMMENDED OLLAMA MODELS FOR TESTING AGENTS")
    print("="*80 + "\n")
    
    for model_id, info in OLLAMA_MODELS.items():
        if info["recommended"]:
            print(f"   {info['name']} ({model_id})")
            print(f"   Size: {info['size']}")
            print(f"   {info['description']}")
            print(f"   Install: ollama pull {model_id}")
            print()
    
    print("="*80 + "\n")


if __name__ == "__main__":
    """Test the helper functions"""
    print("🦙 Ollama Helper - Testing Connection\n")
    
    is_running, models = check_ollama_status()
    
    if is_running:
        print("Ollama is running!")
        if models:
            print(f"\n Installed models ({len(models)}):")
            for model in models:
                print(f"   • {model}")
        else:
            print("\n No models installed yet")
            list_recommended_models()
    else:
        print("Ollama is not running")
        print_ollama_setup_instructions()

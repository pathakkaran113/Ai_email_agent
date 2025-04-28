# Google Search Tool for Agents

This package contains custom Google search tools that can be integrated with your agent. It supports both the Google ADK search and a fallback search implementation using Serper API.

## Setup

1. Install the required dependencies:
   ```bash
   pip install google-generativeai google-adk requests python-dotenv
   ```

2. Set up your API keys in a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   SERPER_API_KEY=your_serper_api_key  # Optional for fallback
   ```

   - Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
   - For fallback search, get a Serper API key from [Serper.dev](https://serper.dev/)

## Files

- `tools/tools.py`: Contains the main search tool implementation
- `test_tools.py`: Test script to verify search functionality
- `agent.py`: Sample agent implementation using the search tool

## Testing

Run the test script to check if your search tools are working:

```bash
python -m multi_tool_agent.test_tools
```

The test script will:
1. Check if your API keys are properly set up
2. Run test searches to verify functionality
3. Report any issues

## Using the Search Tool

### In Your Agent

```python
from multi_tool_agent.tools import custom_google_search

# Define a wrapper for your agent
def search_wrapper(query):
    result = custom_google_search(query)
    if result["status"] == "success":
        return result["results"]["results"]
    else:
        return f"Search failed: {result['error_message']}"

# Add to your agent's tools
search_tool = {
    "name": "search",
    "description": "Searches the web for information",
    "function": search_wrapper
}

# Then add search_tool to your agent's tools list
agent = Agent(
    # ... other parameters
    tools=[search_tool]
)
```

### Standalone Usage

```python
from multi_tool_agent.tools import custom_google_search

# Simple search
result = custom_google_search("What is the capital of France?")
if result["status"] == "success":
    print(result["results"])
else:
    print(f"Search failed: {result['error_message']}")
```

## Troubleshooting

- **API Key Issues**: Make sure your environment variables are correctly set
- **No Results**: Check your internet connection and query formatting
- **Error Response**: Look at the error message for clues about what's wrong

## Features

- Primary search using Google ADK
- Fallback search using Serper API
- Extensive error handling
- Detailed logging for debugging
- Formatted search results 
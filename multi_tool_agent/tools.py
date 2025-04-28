import datetime
import os
import json
import re
import requests
from dotenv import load_dotenv
import openai  # Import OpenAI library
import logging
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService
#from google.adk import api_client

# Load environment variables
load_dotenv()

APP_NAME = "primerole_agent_app"
USER_ID = "default_user"
MODEL = "gemini-2.0-flash"
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()


# client_options = {
#     "timeout": 60.0  # 60 second timeout for generative AI operations
# }

# # Use these options when initializing the client
# genai_client = api_client.ApiClient(
#     api_key=os.getenv("GOOGLE_API_KEY"),
#     client_options=client_options
# )

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def tavily_search(query: str, search_depth: str = "basic", max_results: int = 5) -> dict:
    """
    Searches the web using Tavily API
    
    Args:
        query (str): The search query
        search_depth (str, optional): The search depth ('basic' or 'advanced'). Defaults to "basic".
        max_results (int, optional): Maximum number of results to return. Defaults to 5.
        
    Returns:
        dict: Search results from Tavily
    """
    try:
        # Get API key from environment variables
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            return {
                "status": "error",
                "error_message": "Tavily API key not found in environment variables."
            }
        
        # Convert max_results to int if it's a string
        if isinstance(max_results, str):
            max_results = int(max_results)
            
        # Ensure search_depth is valid
        valid_depths = ["basic", "advanced"]
        if search_depth not in valid_depths:
            search_depth = "basic"
        
        # Tavily API endpoint
        api_url = "https://api.tavily.com/search"
        
        # Request headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
        }
        
        # Make API request
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)  # 30 second timeout
        print(f"tavily_search")
        
        if response.status_code == 200:
            # Parse and extract search results
            results = response.json()
            
            # Format the results
            formatted_results = {
                "status": "success",
                "query": query,
                "results": results.get("results", []),
                "answer": results.get("answer", "")
            }
            
            return formatted_results
        else:
            return {
                "status": "error",
                "error_message": f"Tavily API Error {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Tavily search failed: {str(e)}"
        }

# Define a wrapper for load_memory to fix parameter parsing
def search_memory(query: str, session_id: str = "default_session") -> dict:
    """
    Searches through memory for relevant information
    
    Args:
        query (str): The search query
        session_id (str): Current session ID
        
    Returns:
        dict: Relevant results from memory
    """
    try:
        # Simplified memory search without additional parameters
        results = memory_service.search_memory(query)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "error_message": f"Memory search failed: {str(e)}"}

def get_headers():
    """Returns the common headers needed for PrimeRole API requests"""
    api_key = os.getenv("PRIMEROLE_API_KEY")
    return {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {api_key}',
        'origin': 'https://www.primerole.com',
        'referer': 'https://www.primerole.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

def extract_data(response_json):
    """
    Extracts data from the nested API response structure.
    """
    try:
        if isinstance(response_json, dict):
            # Check for nested data structure
            if "data" in response_json and "organization" in response_json["data"]:
                return response_json["data"]["organization"]
            elif "data" in response_json:
                return response_json["data"]
        return response_json
    except Exception as e:
        return {"error": str(e)}

  

#Updated session storage function
def store_data_in_session(session_id, data_type, data):
    """
    Stores fetched data in the session for later retrieval
    
    Args:
        session_id (str): The ID of the current session
        data_type (str): Type of data being stored (e.g., "contact", "company")
        data (dict): The data to store
    """
    try:
        # Get or create session
        session = session_service.get_session(session_id)
        if not session:
            session = session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=session_id
            )
        
        # Create an event to update the state
        from google.adk.sessions import Event, Content, Part
        
        # Create a state update event
        state_update = {
            data_type: data
        }
        
        # Create the event with the state update
        event = Event(
            author="system",
            content=Content(parts=[Part(text="State update")]),
            state_update=state_update
        )
        
        # Append the event to update the state
        session_service.append_event(session, event)
        
        return True
    except Exception as e:
        logging.error(f"Error storing data in session: {str(e)}")
        return False

# Updated session retrieval function
def retrieve_from_session(session_id, data_type=None, key=None):
    """
    Retrieves data from the session
    
    Args:
        session_id (str): The ID of the current session
        data_type (str, optional): Type of data to retrieve
        key (str, optional): Specific key to retrieve
        
    Returns:
        dict: Retrieved data or empty dict if not found
    """
    try:
        session = session_service.get_session(session_id)
        
        if not session or not session.state:
            return {}
        
        if data_type is None:
            return session.state
        
        if data_type not in session.state:
            return {}
            
        if key is None:
            return session.state[data_type]
        
        # Return specific key
        if key in session.state[data_type]:
            return session.state[data_type][key]
        
        # Try to find by partial match
        for k, v in session.state[data_type].items():
            if key.lower() in k.lower():
                return v
                
        return {}
    
    except Exception as e:
        logging.error(f"Error retrieving from session: {str(e)}")
        return {}

def get_contact_info(contact_id: str, session_id: str = "default_session") -> dict:
    """Retrieves contact information from PrimeRole API using the contact ID.

    Args:
        contact_id (str): The ID of the contact to retrieve information for.
        session_id (str): Current session ID for storing results.

    Returns:
        dict: status and result or error msg.
    """
    # Check if we already have this data in the session
    existing_data = retrieve_from_session(session_id, "contact", contact_id)
    if existing_data:
        return existing_data
    
    try:
        # Get API base URL and headers
        base_url = os.getenv("PRIMEROLE_BASE_URL", "https://api.primerole.com/api/v1")
        api_url = f"{base_url}/contacts/{contact_id}"
        headers = get_headers()
        
        # Make API request
        # In get_company_info function
        response = requests.get(api_url, headers=headers, timeout=20)  # 25 second timeout
        
        if response.status_code == 200:
            # Parse and extract contact data
            contact_data = extract_data(response.json())
            
            result = {
                "status": "success",
                "contact_info": contact_data
            }
            
            # Store in session for future use
            store_data_in_session(session_id, "contact", result)
            
            return result
        else:
            result = {
                "status": "error",
                "error_message": f"API Error {response.status_code}: {response.text}"
            }
            return result
    except Exception as e:
        result = {
            "status": "error",
            "error_message": f"Failed to retrieve contact information: {str(e)}"
        }
        return result
    
def scrape_website(website_url: str, session_id: str = "default_session") -> dict:
    """Scrapes a website using Firecrawl API.

    Args:
        website_url (str): The URL of the website to scrape.
        session_id (str): Current session ID for storing results.
    
    Returns:
        dict: status and result or error msg.
    """
    # Check if we already have this data in the session
    existing_data = retrieve_from_session(session_id, "website", website_url)
    if existing_data:
        return existing_data
    
    try:
        # Get API key from environment variables
        api_key = os.getenv("FIRECRAWL_API_KEY")
        # Use default website URL from .env if none provided
        if not website_url:
            website_url = os.getenv("WEBSITE_URL")
            
        # Firecrawl API endpoint
        api_url = "https://api.firecrawl.dev/v1/scrape"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "url": website_url,
            "formats": ["markdown", "html"],
            "waitFor": 5000,  # Wait for 5 seconds to ensure page loads
            "timeout": 30000  # 30 second timeout
        }
        
        # Make API request
# In scrape_website function
        response = requests.post(api_url, headers=headers, json=payload, timeout=45)  # 45 second timeout (longer since it's scraping)        
        print(f"scrape_website")

        if response.status_code == 200:
            # Parse and extract website data
            response_data = response.json()
            
            # Check if the response is successful
            if not response_data.get("success", False):
                return {
                    "status": "error",
                    "error_message": "Failed to scrape website: API returned unsuccessful response"
                }
            
            # Extract the actual data from the response
            website_data = response_data.get("data", {})
            
            # Store both raw and formatted data
            raw_result = {
                "status": "success",
                "raw_data": website_data,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Format the data for better readability
            formatted_result = {
                "status": "success",
                "website_data": {
                    "Basic Information": {
                        "URL": website_url,
                        "Title": website_data.get("metadata", {}).get("title", "N/A"),
                        "Description": website_data.get("metadata", {}).get("description", "N/A"),
                        "Language": website_data.get("metadata", {}).get("language", "N/A")
                    },
                    "Content": {
                        "Text": website_data.get("content", "N/A"),
                        "Markdown": website_data.get("markdown", "N/A"),
                        "HTML": website_data.get("html", "N/A")
                    },
                    "Links": website_data.get("links", []),
                    "Metadata": website_data.get("metadata", {})
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Store both versions in session
            store_data_in_session(session_id, "website_raw", {website_url: raw_result})
            store_data_in_session(session_id, "website", {website_url: formatted_result})
            
            return formatted_result
        else:
            result = {
                "status": "error",
                "error_message": f"API Error {response.status_code}: {response.text}"
            }
            return result
    except Exception as e:
        result = {
            "status": "error",
            "error_message": f"Failed to scrape website: {str(e)}"
        }
        return result

def get_company_info(company_id: str, session_id: str = "default_session") -> dict:
    """Retrieves company information from PrimeRole API using the company ID, name, or domain and whenever you call this function, it will also call the scrape_website function to get the website data.

    Args:
        company_id (str): The ID, name, or domain of the company to retrieve information for.
        session_id (str): Current session ID for storing results.

    Returns:
        dict: status and result or error msg.
    """
    # Check if we already have this data in the session
    existing_data = retrieve_from_session(session_id, "company", company_id)
    if existing_data:
        return existing_data
    
    try:
        # Get API base URL and headers
        base_url = os.getenv("PRIMEROLE_BASE_URL", "https://api.primerole.com/api/v1")
        
        # Check if input is likely an ID (contains only alphanumeric characters and underscores)
        # and has a specific format (e.g., starts with 'COMP' or 'ORG')
        is_id = (company_id.replace('_', '').isalnum() and 
                (company_id.startswith('COMP') or company_id.startswith('ORG')))
        
        if is_id:
            api_url = f"{base_url}/organizations/{company_id}"
        else:
            # Handle domain or company name
            # Remove any protocol (http://, https://) and www. if present
            domain = company_id.lower().replace('https://', '').replace('http://', '').replace('www.', '')
            # Remove any path after domain
            domain = domain.split('/')[0]
            # If it doesn't end with a TLD, add .com
            if '.' not in domain:
                domain = domain + '.com'
            
            api_url = f"{base_url}/organizations/domain/{domain}"
        
        headers = get_headers()
        
        print(f"Making API request to: {api_url}")  # Debug log
        print(f"karan")
        # Make API request
# In get_contact_info function
        response = requests.get(api_url, headers=headers, timeout=25)  # 20 second timeout         
        print(f"Response status code: {response.status_code}")  # Debug log
        
        if response.status_code == 200:
            # Parse and extract company data
            response_json = response.json()
           # print(f"Response JSON: {response_json}")  # Debug log
            
            company_data = extract_data(response_json)
          #  print(f"Extracted company data: {company_data}")  # Debug log
            
            if not company_data:
                result = {
                    "status": "error",
                    "error_message": "No company data found in the response"
                }
                return result
            
            # Store raw data
            result = {
                "status": "success",
                "company_info": company_data
            }
            store_data_in_session(session_id, "company", {company_id: result})
            
            return result
        elif response.status_code == 404:
            if is_id:
                result = {
                    "status": "error",
                    "error_message": f"Company with ID '{company_id}' not found. Please verify the ID."
                }
            else:
                result = {
                    "status": "error",
                    "error_message": f"No companies found matching '{company_id}'. Please try a different name or domain."
                }
            return result
        else:
            result = {
                "status": "error",
                "error_message": f"API Error {response.status_code}: {response.text}"
            }
            return result
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")  # Debug log
        result = {
            "status": "error",
            "error_message": f"Network error while retrieving company information: {str(e)}"
        }
        return result
    except Exception as e:
        print(f"General exception: {str(e)}")  # Debug log
        result = {
            "status": "error",
            "error_message": f"Failed to retrieve company information: {str(e)}"
        }
        return result

def list_stored_data(session_id: str = "default_session") -> dict:
    """
    Lists all data stored in the session
    
    Args:
        session_id (str): The session ID to retrieve data from
        
    Returns:
        dict: Summary of stored data
    """
    stored_data = retrieve_from_session(session_id)
    
    if not stored_data:
        return {
            "status": "info",
            "message": "No data has been stored in this session yet."
        }
    
    summary = {}
    for data_type, items in stored_data.items():
        if data_type not in ["meta"]:  # Skip metadata
            summary[data_type] = []
            for key, data in items.items():
                # Extract identifying information based on data type
                if data_type == "contact" and "contact_info" in data:
                    info = {"id": key, "name": data["contact_info"].get("name", "Unknown")}
                elif data_type == "company" and "company_info" in data:
                    info = {
                        "name": key,
                        "domain": data["company_info"].get("Basic Information", {}).get("Domain", "Unknown"),
                        "type": "formatted"
                    }
                elif data_type == "company_raw" and "raw_data" in data:
                    info = {
                        "name": key,
                        "type": "raw"
                    }
                elif data_type == "weather":
                    info = {"city": key}
                else:
                    info = {"id": key}
                
                summary[data_type].append(info)
    
    return {
        "status": "success",
        "stored_data": summary
    }


def analyze_company_pain_points(company_name: str, session_id: str = "default_session") -> dict:
    """
    Uses OpenAI to generate pain points and value propositions for a given company
    without relying on web scraping or additional data sources.
    
    Args:
        company_name (str): The name of the company to analyze
        session_id (str): Current session ID for storing results
        
    Returns:
        dict: Pain points and value propositions analysis in a structured format
    """
    import os
    import datetime
    import json
    import openai
    
    # Set the OpenAI API key from environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Check if API key is available
    if not openai.api_key:
        return {
            "status": "error",
            "error_message": "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        }
    
    # Check if we already have this data in the session
    existing_data = retrieve_from_session(session_id, "pain_points", company_name)
    if existing_data:
        return existing_data
    
    try:
        # Create prompt for OpenAI
        system_prompt = """
        You are a business analyst specializing in identifying customer pain points and company value propositions.
        
        For the given company, provide a comprehensive analysis of:
        1. The key pain points (customer problems/challenges) that the company solves
        2. The value propositions the company offers to address these pain points
        
        Format your response like this exact example:

        Here are **pain points [COMPANY] solves** (i.e., customer challenges) and the **value propositions** it offers:
        
        🔧 **Customer Pain Points Solved by [COMPANY]**
        1. **[Pain point 1 as a short phrase]**
           * [One sentence explanation about this challenge]
        2. **[Pain point 2 as a short phrase]**
           * [One sentence explanation about this challenge]
        [Continue with 5-7 total pain points]
        
        💡 **[COMPANY] Value Proposition**
        1. **[Value proposition 1 as a short phrase]**
           * [One sentence explanation of this value]
        2. **[Value proposition 2 as a short phrase]**
           * [One sentence explanation of this value]
        [Continue with 5-9 total value propositions]
        
        End with: "If you want, I can also tailor these for specific use cases — like for **[industry-specific role 1]**, **[industry-specific role 2]**, or **[industry-specific role 3]**."
        
        Important requirements:
        - Be specific and concrete about the company's actual offerings
        - Cover technical, operational, financial, and strategic benefits
        - Use bullet points and emoji formatting exactly as shown
        - Include both the pain point/value title in bold and the explanation
        - Keep explanations concise but informative
        """
        
        user_prompt = f"Please provide a pain point and value proposition analysis for {company_name}."
        
        # Call OpenAI API with the new client format
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        print(f"analyze_company_pain_points")
        # Extract the analysis using the new response format
        analysis_text = response.choices[0].message.content
        
        # Prepare the result
        result = {
            "status": "success",
            "company_name": company_name,
            "analysis": analysis_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Store in session
        store_data_in_session(session_id, "pain_points", {company_name: result})
        
        return result
        
    except Exception as e:
        print(f"Error analyzing pain points: {str(e)}")
        result = {
            "status": "error",
            "error_message": f"Failed to analyze pain points and value propositions: {str(e)}"
        }
        return result
    

    

def add_session_to_memory(session_id):
    """
    Adds a completed session to the memory service for long-term knowledge
    
    Args:
        session_id (str): The ID of the session to add to memory
    """
    try:
        session = session_service.get_session(session_id)
        if session:
            memory_service.add_session_to_memory(session)
            return True
        return False
    except Exception as e:
        logging.error(f"Error adding session to memory: {str(e)}")
        return False

def end_session(session_id):
    """
    Properly ends a session and optionally adds it to memory
    
    Args:
        session_id (str): The ID of the session to end
    """
    try:
        # Add session to memory before deleting
        add_session_to_memory(session_id)
        
        # Delete the session
        session_service.delete_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
        return True
    except Exception as e:
        logging.error(f"Error ending session: {str(e)}")
        return False
    

    

def analyze_customer_basics(company_name: str, session_id: str = "default_session") -> dict:
    """
    Uses OpenAI to get basic customer information

    Args:
        company_name (str): The name of the company to analyze
        session_id (str): Current session ID

    Returns:
        dict: Basic customer information analysis
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        return {
            "status": "error",
            "error_message": "OpenAI API key not found."
        }

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a customer intelligence specialist providing essential business insights.
Extract and organize the following information:
1. Company profile (founding year, leadership, mission)
2. Industry classification and market positioning
3. Core business operations and revenue streams
4. Geographic presence and expansion strategies
5. Company scale (employees, revenue if available, growth trajectory)
6. Key challenges the company might be facing based on their industry and size

FORMAT YOUR RESPONSE WITH:
- Clear section headers (H2 format)
- Facts-only approach with no speculation
- Company-specific information only (no generic industry facts)
- Maximum 250 words total"""
                },
                {
                    "role": "user",
                    "content": f"Please provide basic information about {company_name} as a customer company."
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        print("analyze_customer_basics")
        analysis_text = response.choices[0].message.content
        print(f"analyze_customer_basics")
        return {
            "status": "success",
            "company_name": company_name,
            "analysis": analysis_text
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to analyze customer basics: {str(e)}"
        }






import os
import re

def get_email_template(template_name: str) -> dict:
    """
    Gets the specified email template from the ai_agent_email_templates.txt file.
    
    Args:
        template_name (str): The title of the template (e.g., "Problem → Solution → Action")
        
    Returns:
        dict: Contains the status, template title, and content
    """
    try:
        # Path to the template file (adjust path as needed)
        template_file_path = os.path.join(os.path.dirname(__file__), "ai_agent_email_templates.txt")
        
        with open(template_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Updated regex to match by template title
        # Supports search by just the title, with or without the numeric prefix
       # pattern = rf'\d+\.\s+“{re.escape(template_name)}”.*?(?=\n\d+\.|$)'
        pattern = rf'\d+\.\s+“{re.escape(template_name)}”[\s\S]*?(?=\n\d+\.|$)'

        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return {
                "status": "error",
                "error_message": f"Template '{template_name}' not found."
            }
        
        template_content = match.group(0).strip()
        
        return {
            "status": "success",
            "template_title": template_name,
            "template_content": template_content
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get email template: {str(e)}"
        }


    # Updated session storage function


    

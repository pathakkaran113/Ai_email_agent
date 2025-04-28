# from google.adk.agents.sequential_agent import SequentialAgent , ParallelAgent
# from google.adk.agents.llm_agent import LlmAgent
# from google.genai import types
# from google.adk.sessions import InMemorySessionService
# from google.adk.runners import Runner
# from google.adk.models.lite_llm import LiteLlm


# from .tools import (
#     get_company_info,
#     scrape_website,
#     tavily_search,
#     analyze_company_pain_points,
#     analyze_customer_basics
# )

# # --- Constants ---
# APP_NAME = "sales_email_pipeline_app"
# USER_ID = "dev_user_01"
# SESSION_ID = "pipeline_session_01"
# GEMINI_MODEL = "gemini-1.5-flash"










# # --- Define one agent per tool ---

# # 1. Tavily Search Agent
# tavily_search_agent = LlmAgent(
#     name="TavilySearchAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Research Agent.
#     For the given seller company, search for 3-4 case studies or success stories.
#     Find links that show how the seller company has helped their existing customers.
#     Make ONLY ONE search API call to get all the needed links at once.
#     Format output as a list of top 3-4 relevant links with brief descriptions.
#     """,
#     description="Searches for seller company case studies",
#     tools=[tavily_search],
#     output_key="search_results"
# )

# # 2. Website Scraper Agent
# website_scraper_agent = LlmAgent(
#     name="WebScraperAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Web Scraping Agent.
#     Take the links from 'search_results' and scrape each website.
#     Focus on extracting:
#     - Customer success stories
#     - Case studies and testimonials
#     - How the seller company solved problems for their customers
#     Compile all scraped data into a structured format.
#     """,
#     description="Scrapes websites for seller information",
#     tools=[scrape_website],
#     output_key="scraped_data"
# )

# # 3. Pain Points Analysis Agent
# pain_points_agent = LlmAgent(
#     name="PainPointsAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Pain Points Analysis Agent.
#     Analyze the 'scraped_data' to identify:
#     - Key pain points that the seller company addresses
#     - Clear value propositions they provide
#     - Evidence of problem-solving from case studies
#     Organize your findings in a clear, structured format.
#     - MUST use analyze_company_pain_points tool and do not get it done by data fetched from other agents.
#     """,
#     description="Analyzes seller company's value propositions",
#     tools=[analyze_company_pain_points],
#     output_key="pain_points_analysis"
# )

# # 4. Products Services Agent
# # products_services_agent = LlmAgent(
# #     name="ProductsServicesAgent",
# #     model=GEMINI_MODEL,
# #     instruction="""You are a Products & Services Analysis Agent.
# #     Based on the 'scraped_data', identify:
# #     - Specific product and service names offered by the seller
# #     - Key features and benefits of each product/service
# #     - How these solutions address customer needs
# #     Be specific and comprehensive in your analysis.
# #     """,
# #     description="Analyzes seller company's products and services",
# #     tools=[analyze_products_services],
# #     output_key="products_services_analysis"
# # )

# # 5. Company Info Agent
# company_info_agent = LlmAgent(
#     name="CompanyInfoAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Company Research Agent.
#     For the given customer company, gather comprehensive information using PrimeroleAPI.
#     Collect data on:
#     - Company size, industry, and structure
#     - Recent business developments and news
#     - Key markets and business focus areas
#     - MUST use get_company_info tool and do not get it done by data fetched from other agents.

#     """,
#     description="Gathers information about the customer company",
#     tools=[get_company_info],
#     output_key="company_info"
# )

# # 6. Customer Analysis Agent
# customer_analysis_agent = LlmAgent(
#     name="CustomerAnalysisAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Customer Analysis Agent.
#     Based on the 'company_info', analyze:
#     - Potential business challenges and pain points
#     - Strategic priorities and needs
#     - How the seller's products/services could benefit them
#     - Decision makers and their likely concerns
#     Present insights in a structured format.
#     - MUST use analyze_customer_basics tool and do not get it done by data fetched from other agents.

#     """,
#     description="Analyzes customer company needs",
#     tools=[analyze_customer_basics],
#     output_key="customer_analysis"
# )

# # 7. Email Generation Agent - No external tool, just uses LLM
# email_writer_agent = LlmAgent(
#     name="EmailWriterAgent",
#     model=LiteLlm(model="openai/gpt-4o-mini"),
#     instruction="""You are a Sales Email Writer.
#     Using all the gathered information:
#     - Seller pain points from 'pain_points_analysis'
#     - Seller products from 'products_services_analysis'
#     - Customer information from 'company_info'
#     - Customer needs from 'customer_analysis'
    
#     Write a personalized sales email with these requirements:
#     1. Maximum 100 words , For a 100-word email, this translates to roughly 30 seconds of reading time
#     2. Written in first person from seller's perspective
#     3. Address specific customer pain points
#     4. Mention relevant seller products/services that solve these problems
#     5. Reference case studies/success stories when relevant
#     6. Include a clear call to action
#     7. NO mention of AI, automation or third parties
#     8. strictly do not use any placeholder , get all data yourself from the previous fetched agents
    
#     The email should sound natural, professional and directly from the seller.
#     """,
#     description="Writes the final sales email",
#     output_key="sales_email"
# )

# # --- Create the Root Agent ---
# root_agent = SequentialAgent(
#     name="SalesEmailPipeline",
#     sub_agents=[
#         tavily_search_agent,
#         website_scraper_agent,
#         pain_points_agent,
#         company_info_agent,
#         customer_analysis_agent,
#         email_writer_agent
#     ]
# )



# # Session and Runner setup
# session_service = InMemorySessionService()
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# # Handler function for user input
# def generate_sales_email(input_text):
#     content = types.Content(role='user', parts=[types.Part(text=input_text)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

#     for event in events:
#         if event.is_final_response():
#             final_email = event.content.parts[0].text
#             return final_email

# # Example usage:
# # result = generate_sales_email("seller: Snowflake and customer: Nike")
# # print(result)












































# from google.adk.agents import ParallelAgent
# from google.adk.agents.sequential_agent import SequentialAgent 
# from google.adk.agents.llm_agent import LlmAgent
# from google.genai import types
# from google.adk.sessions import InMemorySessionService
# from google.adk.runners import Runner
# from google.adk.models.lite_llm import LiteLlm


# from .tools import (
#     get_company_info,
#     scrape_website,
#     tavily_search,
#     analyze_company_pain_points,
#     analyze_customer_basics
# )

# # --- Constants ---
# APP_NAME = "sales_email_pipeline_app"
# USER_ID = "dev_user_01"
# SESSION_ID = "pipeline_session_01"
# GEMINI_MODEL = "gemini-1.5-flash"










# # --- Define one agent per tool ---

# # 1. Tavily Search Agent
# tavily_search_agent = LlmAgent(
#     name="TavilySearchAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Research Agent.
#     For the given seller company, search for 3-4 case studies or success stories.
#     Find links that show how the seller company has helped their existing customers.
#     Make ONLY ONE search API call to get all the needed links at once.
#     Format output as a list of top 3-4 relevant links with brief descriptions.
#     """,
#     description="Searches for seller company case studies",
#     tools=[tavily_search],
#     output_key="search_results"
# )

# # 2. Website Scraper Agent
# website_scraper_agent = LlmAgent(
#     name="WebScraperAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Web Scraping Agent.
#     Take the links from 'search_results' and scrape each website.
#     Focus on extracting:
#     - Customer success stories
#     - Case studies and testimonials
#     - How the seller company solved problems for their customers
#     Compile all scraped data into a structured format.
#     """,
#     description="Scrapes websites for seller information",
#     tools=[scrape_website],
#     output_key="scraped_data"
# )

# # 3. Pain Points Analysis Agent
# pain_points_agent = LlmAgent(
#     name="PainPointsAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Pain Points Analysis Agent.
#     Analyze the 'scraped_data' to identify:
#     - Key pain points that the seller company addresses
#     - Clear value propositions they provide
#     - Evidence of problem-solving from case studies
#     Organize your findings in a clear, structured format.
#     - MUST use analyze_company_pain_points tool and do not get it done by data fetched from other agents.
#     """,
#     description="Analyzes seller company's value propositions",
#     tools=[analyze_company_pain_points],
#     output_key="pain_points_analysis"
# )

# # 4. Products Services Agent
# # products_services_agent = LlmAgent(
# #     name="ProductsServicesAgent",
# #     model=GEMINI_MODEL,
# #     instruction="""You are a Products & Services Analysis Agent.
# #     Based on the 'scraped_data', identify:
# #     - Specific product and service names offered by the seller
# #     - Key features and benefits of each product/service
# #     - How these solutions address customer needs
# #     Be specific and comprehensive in your analysis.
# #     """,
# #     description="Analyzes seller company's products and services",
# #     tools=[analyze_products_services],
# #     output_key="products_services_analysis"
# # )

# # 5. Company Info Agent
# company_info_agent = LlmAgent(
#     name="CompanyInfoAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Company Research Agent.
#     For the given customer company, gather comprehensive information using PrimeroleAPI.
#     Collect data on:
#     - Company size, industry, and structure
#     - Recent business developments and news
#     - Key markets and business focus areas
#     - MUST use get_company_info tool and do not get it done by data fetched from other agents.

#     """,
#     description="Gathers information about the customer company",
#     tools=[get_company_info],
#     output_key="company_info"
# )

# # 6. Customer Analysis Agent
# customer_analysis_agent = LlmAgent(
#     name="CustomerAnalysisAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Customer Analysis Agent.
#     Based on the 'company_info', analyze:
#     - Potential business challenges and pain points
#     - Strategic priorities and needs
#     - How the seller's products/services could benefit them
#     - Decision makers and their likely concerns
#     Present insights in a structured format.
#     - MUST use analyze_customer_basics tool and do not get it done by data fetched from other agents.

#     """,
#     description="Analyzes customer company needs",
#     tools=[analyze_customer_basics],
#     output_key="customer_analysis"
# )

# # 7. Email Generation Agent - No external tool, just uses LLM
# email_writer_agent = LlmAgent(
#     name="EmailWriterAgent",
#     model=LiteLlm(model="openai/gpt-4o"),
#     instruction="""You are a Sales Email Writer.
#     Using all the gathered information:
#     - Seller pain points from 'pain_points_analysis'
#     - Seller products from 'products_services_analysis'
#     - Customer information from 'company_info'
#     - Customer needs from 'customer_analysis'
    
#     Write a personalized sales email with these requirements:
#     1. Maximum 100 words , For a 100-word email, this translates to roughly 30 seconds of reading time
#     2. Written in first person from seller's perspective
#     3. Address specific customer pain points
#     4. Mention relevant seller products/services that solve these problems
#     5. Reference case studies/success stories when relevant
#     6. Include a clear call to action
#     7. NO mention of AI, automation or third parties
#     8. strictly do not use any placeholder , get all data yourself from the previous fetched agents
    
#     The email should sound natural, professional and directly from the seller.
#     """,
#     description="Writes the final sales email",
#     output_key="sales_email"
# )

# # --- Create the Root Agent ---

# pa1 = SequentialAgent(
#     name="pa1",
#     sub_agents=[
#         tavily_search_agent,website_scraper_agent
#     ]
# )

# pa2 = SequentialAgent(
#     name="pa1",
#     sub_agents=[
#         pain_points_agent
#     ]
# )

# pa3 = SequentialAgent(
#     name="pa1",
#     sub_agents=[
#         company_info_agent
#     ]
# )

# pa4 = SequentialAgent(
#     name="pa1",
#     sub_agents=[
#         customer_analysis_agent
#     ]
# )


# root_agentkp = ParallelAgent(
#     name="real_root",
#     sub_agents=[pa1,pa2,pa3,pa4]
# )



# root_agent = SequentialAgent(
#     name="SalesEmailPipeline",
#     sub_agents=[
#         root_agentkp,
#         email_writer_agent
#     ]
# )


# # Session and Runner setup
# session_service = InMemorySessionService()
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# # Handler function for user input
# def generate_sales_email(input_text):
#     content = types.Content(role='user', parts=[types.Part(text=input_text)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

#     for event in events:
#         if event.is_final_response():
#             final_email = event.content.parts[0].text
#             return final_email

# # Example usage:
# # result = generate_sales_email("seller: Snowflake and customer: Nike")
# # print(result)









































from google.adk.agents import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent 
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm


from .tools import (
    get_company_info,
    scrape_website,
    tavily_search,
    analyze_company_pain_points,
    analyze_customer_basics
)

# --- Constants ---
APP_NAME = "sales_email_pipeline_app"
USER_ID = "dev_user_01"
SESSION_ID = "pipeline_session_01"
GEMINI_MODEL = "gemini-1.5-flash"










# --- Define one agent per tool ---

# 1. Tavily Search Agent
tavily_search_agent = LlmAgent(
    name="TavilySearchAgent",
    model=GEMINI_MODEL,
    instruction = """
You are a Research Agent.
For the given seller company, search for 3-4 case studies or success stories.
Find links that show how the seller company has helped any of its existing customers—excluding the customer company mentioned in the prompt.
Make ONLY ONE search API call to get all the needed links at once.
Format output as a list of top 3-4 relevant links with brief descriptions of how the seller helped those companies.
""",
    description="Searches for seller company case studies",
    tools=[tavily_search],
    output_key="search_results"
)

# 2. Website Scraper Agent
website_scraper_agent = LlmAgent(
    name="WebScraperAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Web Scraping Agent.
    Take the links from 'search_results' and scrape each website.
    Focus on extracting:
    - Customer success stories
    - Case studies and testimonials
    - How the seller company solved problems for their customers
    -Or get the data which found useful
    """,
    description="Scrapes websites for seller information",
    tools=[scrape_website],
    output_key="scraped_data"
)

# 3. Pain Points Analysis Agent
pain_points_agent = LlmAgent(
    name="PainPointsAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Pain Points Analysis Agent.
    Analyze the 'scraped_data' to identify:
    - Key pain points that the seller company addresses
    - Clear value propositions they provide
    - Evidence of problem-solving from case studies
    Organize your findings in a clear, structured format.
    - MUST use analyze_company_pain_points tool and do not get it done by data fetched from other agents.
    """,
    description="Analyzes seller company's value propositions",
    tools=[analyze_company_pain_points],
    output_key="pain_points_analysis"
)

# 4. Products Services Agent
# products_services_agent = LlmAgent(
#     name="ProductsServicesAgent",
#     model=GEMINI_MODEL,
#     instruction="""You are a Products & Services Analysis Agent.
#     Based on the 'scraped_data', identify:
#     - Specific product and service names offered by the seller
#     - Key features and benefits of each product/service
#     - How these solutions address customer needs
#     Be specific and comprehensive in your analysis.
#     """,
#     description="Analyzes seller company's products and services",
#     tools=[analyze_products_services],
#     output_key="products_services_analysis"
# )

# 5. Company Info Agent
company_info_agent = LlmAgent(
    name="CompanyInfoAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Company Research Agent.
    For the given customer company, gather comprehensive information using PrimeroleAPI.
    Collect data on:
    - Company size, industry, and structure
    - Recent business developments and news
    - Key markets and business focus areas
    - MUST use get_company_info tool and do not get it done by data fetched from other agents.

    """,
    description="Gathers information about the customer company",
    tools=[get_company_info],
    output_key="company_info"
)

# 6. Customer Analysis Agent
customer_analysis_agent = LlmAgent(
    name="CustomerAnalysisAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Customer Analysis Agent.
    Based on the 'company_info', analyze:
    - Potential business challenges and pain points
    - Strategic priorities and needs
    - How the seller's products/services could benefit them
    - Decision makers and their likely concerns
    Present insights in a structured format.
    - MUST use analyze_customer_basics tool and do not get it done by data fetched from other agents.

    """,
    description="Analyzes customer company needs",
    tools=[analyze_customer_basics],
    output_key="customer_analysis"
)

# 7. Email Generation Agent - No external tool, just uses LLM
email_writer_agent = LlmAgent(
    name="EmailWriterAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction="""
    You are a Sales Email Writer.
    Using all the gathered information, including a template:
    - Seller pain points from 'pain_points_analysis'
    - Seller products from 'products_services_analysis'
    - Customer information from 'company_info'
    - Customer needs from 'customer_analysis'
    
    Write the sales email in the following format:

    Hi [customer_name],
    
    I came across your profile when looking for leaders in the [customer_industry] space. I work with leaders like you facing [problem 1] and [problem 2].
    
    [seller_name] offers [solution_1] and [solution_2] to address these problems which usually results in [metric_1 improvement] and [metric_2 improvement].
    
    I would love to connect with you, understand your problems, and see how we can be of help. Does something this week sound good to have a chat?
    
    Thanks,
    
    In this email:
    - Replace [problem 1] and [problem 2] with the actual pain points identified in 'pain_points_analysis'.
    - Replace [solution 1] and [solution 2] with the products or services that address these pain points from 'products_services_analysis'.
    - Replace [metric_1 improvement] and [metric_2 improvement] with quantifiable improvements that were mentioned in the case studies or customer success stories, where available.
    - Replace [customer_name], [customer_industry], and [seller_name] with actual values from the customer and seller data.
    - **DO NOT use placeholders.** All values should come from the actual data processed by the previous agents.

    Make sure the email is:
    - Maximum 100 words
    - Written in first person from the seller's perspective
    - Address specific customer pain points
    - Mention relevant seller products/services
    - Reference case studies/success stories
    - Include a clear call to action
    - Do not use placeholders, use actual data only
    - contains a problem and its solution that customer is facing or might face in the future.
    - you are getting a very high amount of data please use the data , numbers in the mail.
    """,
    description="Writes the final sales email using a template and actual data",
    output_key="sales_email"
)


# --- Create the Root Agent ---

pa1 = SequentialAgent(
    name="pa1",
    sub_agents=[
        tavily_search_agent,website_scraper_agent
    ]
)

pa2 = SequentialAgent(
    name="pa2",
    sub_agents=[
        pain_points_agent
    ]
)

pa3 = SequentialAgent(
    name="pa3",
    sub_agents=[
        company_info_agent
    ]
)

pa4 = SequentialAgent(
    name="pa4",
    sub_agents=[
        customer_analysis_agent
    ]
)


root_agentkp = ParallelAgent(
    name="real_root",
    sub_agents=[pa1,pa2,pa3,pa4]
)



root_agent = SequentialAgent(
    name="SalesEmailPipeline",
    sub_agents=[
        root_agentkp,
        email_writer_agent
    ]
)


# Session and Runner setup
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# Handler function for user input
def generate_sales_email(input_text):
    content = types.Content(role='user', parts=[types.Part(text=input_text)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_email = event.content.parts[0].text
            return final_email

# Example usage:
# result = generate_sales_email("seller: Snowflake and customer: Nike")
# print(result)





"""
Property Analysis Agent - AI-powered analysis of property investments
"""
import json
import os
import asyncio
import streamlit as st
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class PropertyAnalysisAgent:
    """
    AI-powered property analysis agent that evaluates investment opportunities
    and provides recommendations based on property data
    """
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Default model
        self.results = []
        
    def set_model(self, model_name: str) -> None:
        """Set the OpenAI model to use for analysis"""
        self.model = model_name
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def analyze_properties(_self, properties_json: str, locations_json: str, temperature: float = 0.2):
        """
        Analyze properties to identify top investment opportunities
        This function is cached to avoid repeated API calls
        """
        with st.spinner("Analyzing properties to find top investment opportunities..."):
            # Prepare context for the LLM
            system_prompt = """You are a real estate analysis expert specializing in property investments. 
            Your task is to analyze a set of properties and recommend the best investments based on multiple factors."""
            
            user_prompt = f"""Analyze these properties and provide a ranked list of the top 5 best investment opportunities:

            Property Data:
            {properties_json}

            Location Analysis:
            {locations_json}

            Consider the following factors in your analysis:
            1. Price per square yard compared to location average
            2. Location growth potential and development
            3. Property features and amenities
            4. Ownership type and transaction ease
            5. Overall value for money

            For each recommended property, provide:
            1. Property title and basic details
            2. Price and size information
            3. Location advantages
            4. Specific reasons why it's a good investment
            5. Any considerations or potential drawbacks

            Format your response as a well-structured JSON with this format:
            {{
                "top_properties": [
                    {{
                        "rank": 1,
                        "title": "Property title",
                        "details": "Basic property details",
                        "price_info": "Price and value analysis",
                        "location_advantages": "Why this location is good",
                        "investment_rationale": "Why this is a good investment",
                        "considerations": "Things to keep in mind"
                    }},
                    // more properties...
                ]
            }}
            """
            
            try:
                response = _self.client.chat.completions.create(
                    model=_self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                analysis_result = json.loads(response.choices[0].message.content)
                return analysis_result.get("top_properties", [])
                
            except Exception as e:
                st.error(f"Error analyzing properties: {str(e)}")
                return []
    
    def run_analysis(self, properties: List[Dict], location_stats: Dict) -> List[Dict]:
        """
        Run analysis on properties and return recommendations
        """
        # Use only first 30 properties to maintain consistent cache key
        properties_subset = properties[:30] if len(properties) > 30 else properties
        
        # Serialize the inputs for the analysis function
        properties_json = json.dumps(properties_subset, indent=2)
        locations_json = json.dumps(location_stats, indent=2)
        
        # Call the cached analysis function
        self.results = self.analyze_properties(properties_json, locations_json)
        return self.results

def display_analysis_ui(dashboard):
    """
    Display UI elements for the property analysis agent
    """
    st.header("AI Property Analysis")
    
    # Check if the analysis agent is enabled in session state
    if 'analysis_enabled' not in st.session_state:
        st.session_state['analysis_enabled'] = False
    
    # Create a button to toggle the analysis agent
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(
            "Run Analysis" if not st.session_state['analysis_enabled'] else "Hide Analysis", 
            key="toggle_analysis"
        ):
            st.session_state['analysis_enabled'] = not st.session_state['analysis_enabled']
            if st.session_state['analysis_enabled']:
                st.session_state['analysis_results'] = None  # Clear previous results
    
    with col2:
        if st.session_state['analysis_enabled']:
            st.info("AI analysis is active - analyzing properties for investment opportunities")
        else:
            st.info("AI analysis is disabled - click the button to analyze properties")
    
    # If analysis is enabled, run and show results
    if st.session_state['analysis_enabled']:
        if 'analysis_results' not in st.session_state or not st.session_state['analysis_results']:
            # Create and run the analysis agent
            agent = PropertyAnalysisAgent()
            
            # Add model selection
            model_options = ["gpt-4o-mini", "gpt-3.5-turbo"]
            selected_model = st.selectbox("Select AI model:", model_options, index=0)
            agent.set_model(selected_model)
            
            # Run analysis 
            results = agent.run_analysis(dashboard.all_properties, dashboard.location_stats)
            
            # Save results to session state
            st.session_state['analysis_results'] = results
        
        # Display results
        results = st.session_state['analysis_results']
        display_analysis_results(results)

def display_analysis_results(results):
    """
    Display the analysis results in a structured format
    """
    if not results:
        st.warning("No investment recommendations could be generated. Try modifying your search criteria.")
        return
        
    st.subheader("Top Investment Recommendations")
    
    for prop in results:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### Rank #{prop['rank']}")
            with col2:
                st.markdown(f"### {prop['title']}")
            
            st.markdown(f"**Details:** {prop['details']}")
            st.markdown(f"**Price Info:** {prop['price_info']}")
            st.markdown(f"**Location Advantages:** {prop['location_advantages']}")
            st.markdown(f"**Investment Rationale:** {prop['investment_rationale']}")
            st.markdown(f"**Considerations:** {prop['considerations']}")
            st.divider()

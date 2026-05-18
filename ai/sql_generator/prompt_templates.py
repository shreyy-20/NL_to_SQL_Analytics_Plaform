"""
Prompt templates for SQL generation using LLMs
Optimized for agricultural queries in Indian context
"""

from typing import Dict, Any

class SQLPromptTemplates:
    """Collection of prompts for different query types"""
    
    # Database schema description
    DB_SCHEMA = """
    Database Schema for KrishiQuery (Indian Agriculture System):
    
    Table: farmers
    - farmer_id (INT, PRIMARY KEY): Unique farmer identifier
    - name (VARCHAR): Farmer's full name
    - phone (VARCHAR): 10-digit mobile number
    - village (VARCHAR): Village name
    - district (VARCHAR): District in Odisha
    - state (VARCHAR): Always 'Odisha'
    - land_size (FLOAT): Land in hectares
    - created_at (TIMESTAMP)
    - updated_at (TIMESTAMP)
    
    Table: pmkisan_payments
    - id (INT, PRIMARY KEY)
    - farmer_id (INT, FOREIGN KEY -> farmers.farmer_id)
    - amount (DECIMAL): Payment amount in INR (typically 2000 or 6000)
    - payment_date (DATE)
    - status (VARCHAR): 'pending', 'processed', 'completed', 'failed'
    - transaction_id (VARCHAR)
    - installment_number (INT): 1, 2, or 3 for the year
    
    Table: kalia_payments
    - id (INT, PRIMARY KEY)
    - farmer_id (INT, FOREIGN KEY -> farmers.farmer_id)
    - amount (DECIMAL): Payment amount in INR
    - payment_date (DATE)
    - status (VARCHAR): 'pending', 'processed', 'completed', 'failed'
    - transaction_id (VARCHAR)
    - scheme_type (VARCHAR): 'input_subsidy', 'livelihood_support', 'life_insurance'
    
    Table: soil_health
    - id (INT, PRIMARY KEY)
    - farmer_id (INT, FOREIGN KEY -> farmers.farmer_id)
    - nitrogen (FLOAT): Nitrogen content in kg/ha
    - phosphorus (FLOAT): Phosphorus content in kg/ha
    - potassium (FLOAT): Potassium content in kg/ha
    - ph (FLOAT): Soil pH (0-14 scale)
    - organic_carbon (FLOAT): Organic carbon percentage
    - test_date (DATE)
    - recommendation (TEXT): Expert recommendations
    
    Table: mandi_prices
    - id (INT, PRIMARY KEY)
    - crop (VARCHAR): Crop name (e.g., 'paddy', 'wheat')
    - market (VARCHAR): Mandi name
    - district (VARCHAR): District name
    - price (DECIMAL): Price in INR per quintal
    - date (DATE)
    - variety (VARCHAR): Crop variety if available
    - grade (VARCHAR): Quality grade
    
    Table: weather
    - id (INT, PRIMARY KEY)
    - village (VARCHAR): Village name
    - district (VARCHAR): District name
    - date (DATE)
    - rainfall (FLOAT): Rainfall in mm
    - temperature (FLOAT): Temperature in Celsius
    - forecast (TEXT): Weather description
    - humidity (FLOAT): Humidity percentage
    
    Important Notes:
    - Amounts are in Indian Rupees (INR)
    - Land size is in hectares (1 hectare = 2.47 acres)
    - Mandi prices are per quintal (1 quintal = 100 kg)
    - PM-KISAN gives ₹6000/year in 3 installments of ₹2000 each
    """
    
    # Intent-specific prompt templates
    PROMPTS = {
        "PAYMENT": """
        You are an expert SQL query generator for agricultural data.
        
        Database Schema:
        {schema}
        
        User Question: "{question}"
        Farmer ID: {farmer_id}
        
        Generate a SQL query to fetch payment information. The query should:
        1. Only use SELECT statements (no INSERT, UPDATE, DELETE)
        2. Show payment amounts, dates, and status
        3. Order by payment date descending
        4. Handle both PM-KISAN and KALIA schemes
        
        Generate only the SQL query, no explanation:
        """,
        
        "PRICE": """
        You are an expert SQL query generator for mandi price data.
        
        Database Schema:
        {schema}
        
        User Question: "{question}"
        Extracted entities: {entities}
        
        Generate a SQL query to fetch mandi prices. The query should:
        1. Only use SELECT statements
        2. Filter by crop name if mentioned
        3. Filter by market/location if mentioned
        4. Order by date descending to get latest prices
        5. Limit to 5-10 most recent entries
        
        Generate only the SQL query, no explanation:
        """,
        
        "SOIL": """
        You are an expert SQL query generator for soil health data.
        
        Database Schema:
        {schema}
        
        User Question: "{question}"
        Farmer ID: {farmer_id}
        
        Generate a SQL query to fetch soil health information. The query should:
        1. Only use SELECT statements
        2. Get the most recent soil test report
        3. Include all soil parameters (N, P, K, pH)
        4. Include recommendations if available
        
        Generate only the SQL query, no explanation:
        """,
        
        "WEATHER": """
        You are an expert SQL query generator for weather data.
        
        Database Schema:
        {schema}
        
        User Question: "{question}"
        Location: {location}
        
        Generate a SQL query to fetch weather information. The query should:
        1. Only use SELECT statements
        2. Filter by location (village or district)
        3. Filter by date range (today, upcoming days)
        4. Include rainfall, temperature, and forecast
        5. Order by date ascending
        
        Generate only the SQL query, no explanation:
        """
    }
    
    # Response formatting templates
    RESPONSE_TEMPLATES = {
        "PAYMENT": """
        Based on the query results:
        - Total payments received: ₹{total_amount}
        - Number of payments: {payment_count}
        - Latest payment: ₹{latest_amount} on {latest_date}
        - Status: {latest_status}
        
        Format as a friendly message in {language} explaining the payment status.
        """,
        
        "PRICE": """
        Based on the mandi price data:
        - Crop: {crop}
        - Market: {market}
        - Current price: ₹{price} per quintal
        - Date: {date}
        
        Provide price information in {language} with context about whether the price is good or average.
        """,
        
        "SOIL": """
        Based on the soil health report:
        - Test date: {test_date}
        - Nitrogen (N): {nitrogen} kg/ha
        - Phosphorus (P): {phosphorus} kg/ha
        - Potassium (K): {potassium} kg/ha
        - pH level: {ph}
        - Recommendations: {recommendation}
        
        Explain the soil health status in {language} and provide actionable advice.
        """,
        
        "WEATHER": """
        Weather forecast:
        {forecast_data}
        
        Provide weather information in {language} focusing on rainfall forecast and temperature.
        """
    }
    
    # Few-shot examples for in-context learning
    FEW_SHOT_EXAMPLES = {
        "PAYMENT": [
            {
                "question": "मेरी PM-KISAN की किश्त आई क्या?",
                "sql": """
                SELECT 
                    'PM-KISAN' as scheme_name,
                    amount,
                    payment_date,
                    status,
                    installment_number
                FROM pmkisan_payments
                WHERE farmer_id = 123
                ORDER BY payment_date DESC
                LIMIT 5;
                """
            },
            {
                "question": "मुझे KALIA से कितना पैसा मिला है?",
                "sql": """
                SELECT 
                    scheme_type,
                    SUM(amount) as total_amount,
                    COUNT(*) as payment_count,
                    MAX(payment_date) as last_payment_date
                FROM kalia_payments
                WHERE farmer_id = 123
                GROUP BY scheme_type;
                """
            }
        ],
        "PRICE": [
            {
                "question": "भुवनेश्वर में धान का भाव क्या है?",
                "sql": """
                SELECT crop, market, price, date, district
                FROM mandi_prices
                WHERE crop ILIKE '%paddy%' 
                    AND (market ILIKE '%bhubaneswar%' OR district ILIKE '%khordha%')
                ORDER BY date DESC
                LIMIT 5;
                """
            }
        ],
        "SOIL": [
            {
                "question": "मेरी मिट्टी की रिपोर्ट दिखाओ",
                "sql": """
                SELECT nitrogen, phosphorus, potassium, ph, 
                       organic_carbon, test_date, recommendation
                FROM soil_health
                WHERE farmer_id = 123
                ORDER BY test_date DESC
                LIMIT 1;
                """
            }
        ],
        "WEATHER": [
            {
                "question": "अगले हफ्ते बारिश होगी क्या?",
                "sql": """
                SELECT date, rainfall, temperature, forecast
                FROM weather
                WHERE date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                ORDER BY date;
                """
            }
        ]
    }
    
    @classmethod
    def get_prompt(cls, intent: str, question: str, **kwargs) -> str:
        """Get formatted prompt for specific intent"""
        if intent not in cls.PROMPTS:
            intent = "PAYMENT"  # default
        
        prompt_template = cls.PROMPTS[intent]
        
        # Add few-shot examples if available
        if intent in cls.FEW_SHOT_EXAMPLES:
            examples = cls.FEW_SHOT_EXAMPLES[intent]
            example_text = "\n\nExamples:\n"
            for ex in examples:
                example_text += f"Question: {ex['question']}\nSQL: {ex['sql']}\n"
            prompt_template = example_text + "\n" + prompt_template
        
        return prompt_template.format(
            schema=cls.DB_SCHEMA,
            question=question,
            **kwargs
        )
    
    @classmethod
    def get_response_template(cls, intent: str, language: str = "hi") -> str:
        """Get response formatting template"""
        template = cls.RESPONSE_TEMPLATES.get(intent, cls.RESPONSE_TEMPLATES["PAYMENT"])
        return template.format(language=language)
    
    @classmethod
    def get_database_description(cls) -> str:
        """Get full database schema description"""
        return cls.DB_SCHEMA

# Helper functions
def get_sql_prompt(intent: str, question: str, farmer_id: int = None, entities: dict = None) -> str:
    """Convenience function to get SQL generation prompt"""
    return SQLPromptTemplates.get_prompt(
        intent=intent,
        question=question,
        farmer_id=farmer_id or "{{farmer_id}}",
        entities=entities or {}
    )

def get_response_format(intent: str, language: str = "hi") -> str:
    """Convenience function to get response format instruction"""
    return SQLPromptTemplates.get_response_template(intent, language)
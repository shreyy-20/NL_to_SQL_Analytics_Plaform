"""
SQL Generator using CodeLlama or GPT
Converts natural language to SQL for agricultural queries
"""

import logging
import re
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
import os

from ai.sql_generator.prompt_templates import SQLPromptTemplates, get_sql_prompt
from ai.sql_generator.validator import SQLValidator

logger = logging.getLogger(__name__)

class SQLGenerator:
    """Generate SQL queries from natural language"""
    
    def __init__(self, model_type: Optional[str] = None):
        # Default to 'template' to prevent massive LLM loading delays on Render
        self.model_type = model_type or os.getenv("SQL_MODEL_TYPE", "template")
        self.validator = SQLValidator()
        self._model = None
        self._tokenizer = None
        
    def _load_model(self):
        """Load the SQL generation model (CodeLlama or similar)"""
        if self._model is not None:
            return
        
        try:
            if self.model_type == "local":
                # Try to load CodeLlama
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                model_name = "codellama/CodeLlama-7b-Instruct-hf"
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    load_in_8bit=True  # Use 8-bit quantization for memory efficiency
                )
                logger.info(f"Loaded {model_name} for SQL generation")
            else:
                # Use API-based model (GPT, etc.)
                logger.info(f"Using API-based model: {self.model_type}")
                
        except Exception as e:
            logger.warning(f"Failed to load local model: {e}, falling back to template-based generation")
            self.model_type = "template"
    
    def generate(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        farmer_id: Optional[int] = None,
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            intent: Classified intent (PAYMENT, PRICE, SOIL, WEATHER)
            entities: Extracted entities (crop, location, etc.)
            farmer_id: Farmer ID if available
            language: Language code
        
        Returns:
            Dictionary with sql_query, validated flag, and errors
        """
        try:
            # Build prompt
            prompt = self._build_prompt(question, intent, entities, farmer_id, language)
            
            # Generate SQL
            if self.model_type == "local" and self._model:
                sql_query = self._generate_with_local_model(prompt)
            elif self.model_type == "template":
                sql_query = self._generate_with_template(intent, farmer_id, entities)
            else:
                sql_query = self._generate_with_api(prompt)
            
            # Clean and validate SQL
            sql_query = self._clean_sql(sql_query)
            
            # Validate
            validation_result = self.validator.validate(sql_query)
            
            return {
                "sql_query": sql_query,
                "validated": validation_result["is_valid"],
                "confidence": 0.8 if validation_result["is_valid"] else 0.3,
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"],
                "query_type": validation_result["query_type"],
                "tables_accessed": validation_result["tables_accessed"]
            }
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            # Fallback to safe template
            fallback_sql = self._get_fallback_sql(intent, farmer_id)
            return {
                "sql_query": fallback_sql,
                "validated": True,
                "confidence": 0.5,
                "errors": [str(e)],
                "warnings": [],
                "query_type": "SELECT",
                "tables_accessed": []
            }
    
    def _build_prompt(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        farmer_id: Optional[int],
        language: str
    ) -> str:
        """Build the prompt for SQL generation"""
        
        # Get base prompt
        base_prompt = get_sql_prompt(
            intent=intent,
            question=question,
            farmer_id=farmer_id,
            entities=entities
        )
        
        # Add language instruction
        language_instruction = f"\nRespond in English SQL syntax only, not in {language} language.\n"
        
        # Add safety instruction
        safety_instruction = """
        Important Safety Rules:
        - Generate ONLY SELECT queries
        - Do NOT generate INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE
        - Use parameterized queries (no direct string concatenation)
        - Always use proper WHERE clauses to limit results
        - Add LIMIT clause for large result sets
        """
        
        return base_prompt + language_instruction + safety_instruction
    
    def _generate_with_local_model(self, prompt: str) -> str:
        """Generate SQL using local CodeLlama model"""
        try:
            inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
            
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.1,  # Low temperature for deterministic output
                do_sample=False,
                num_beams=4
            )
            
            sql = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the SQL part (remove prompt)
            sql = sql[len(prompt):].strip()
            return sql
            
        except Exception as e:
            logger.error(f"Local model generation failed: {e}")
            raise
    
    def _generate_with_api(self, prompt: str) -> str:
        """Generate SQL using API-based model (OpenAI or similar)"""
        # This would integrate with OpenAI API or similar
        # For now, fallback to template
        logger.warning("API model not configured, using template fallback")
        raise Exception("API model not configured")
    
    def _generate_with_template(
        self,
        intent: str,
        farmer_id: Optional[int],
        entities: Dict[str, Any]
    ) -> str:
        """Generate SQL using predefined templates"""
        
        if intent == "PAYMENT":
            if farmer_id:
                return f"""
                SELECT 
                    'PM-KISAN' as scheme_name,
                    amount,
                    payment_date,
                    status,
                    installment_number
                FROM pmkisan_payments
                WHERE farmer_id = {farmer_id}
                
                UNION ALL
                
                SELECT 
                    CONCAT('KALIA-', scheme_type) as scheme_name,
                    amount,
                    payment_date,
                    status,
                    NULL as installment_number
                FROM kalia_payments
                WHERE farmer_id = {farmer_id}
                
                ORDER BY payment_date DESC
                LIMIT 10;
                """
            else:
                return "SELECT 'Farmer ID required' as message;"
        
        elif intent == "PRICE":
            crop = entities.get("crop", "").lower()
            location = entities.get("location", "").lower()
            
            conditions = []
            if crop:
                conditions.append(f"crop ILIKE '%{crop}%'")
            if location:
                conditions.append(f"(market ILIKE '%{location}%' OR district ILIKE '%{location}%')")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            return f"""
            SELECT crop, market, district, price, date, variety
            FROM mandi_prices
            WHERE {where_clause}
            ORDER BY date DESC
            LIMIT 10;
            """
        
        elif intent == "SOIL":
            if farmer_id:
                return f"""
                SELECT nitrogen, phosphorus, potassium, ph, organic_carbon,
                       test_date, recommendation
                FROM soil_health
                WHERE farmer_id = {farmer_id}
                ORDER BY test_date DESC
                LIMIT 1;
                """
            else:
                return "SELECT 'Farmer ID required' as message;"
        
        elif intent == "WEATHER":
            location = entities.get("location", "")
            if location:
                return f"""
                SELECT date, rainfall, temperature, forecast, humidity
                FROM weather
                WHERE (village ILIKE '%{location}%' OR district ILIKE '%{location}%')
                    AND date >= CURRENT_DATE
                ORDER BY date
                LIMIT 7;
                """
            else:
                return """
                SELECT date, rainfall, temperature, forecast, humidity
                FROM weather
                WHERE date >= CURRENT_DATE
                ORDER BY date
                LIMIT 7;
                """
        
        else:
            return "SELECT 'Unsupported query type' as message;"
    
    def _get_fallback_sql(self, intent: str, farmer_id: Optional[int]) -> str:
        """Get safe fallback SQL query"""
        if intent == "PAYMENT" and farmer_id:
            return f"""
            SELECT 'PM-KISAN' as scheme_name, amount, payment_date, status
            FROM pmkisan_payments
            WHERE farmer_id = {farmer_id}
            ORDER BY payment_date DESC
            LIMIT 5;
            """
        elif intent == "SOIL" and farmer_id:
            return f"""
            SELECT nitrogen, phosphorus, potassium, ph, recommendation
            FROM soil_health
            WHERE farmer_id = {farmer_id}
            ORDER BY test_date DESC
            LIMIT 1;
            """
        elif intent == "PRICE":
            return """
            SELECT crop, market, price, date
            FROM mandi_prices
            ORDER BY date DESC
            LIMIT 5;
            """
        else:
            return "SELECT 'No data available' as message;"
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and format generated SQL"""
        # Remove markdown code blocks if present
        sql = re.sub(r'```sql\n?', '', sql)
        sql = re.sub(r'```\n?', '', sql)
        
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        
        # Ensure it starts with SELECT
        if not sql.upper().strip().startswith('SELECT'):
            # Try to find SELECT statement
            select_match = re.search(r'(SELECT\s+.*?)(?:;|$)', sql, re.IGNORECASE | re.DOTALL)
            if select_match:
                sql = select_match.group(1)
            else:
                sql = "SELECT 'Invalid SQL generated' as message;"
        
        # Ensure semicolon at end
        if not sql.rstrip().endswith(';'):
            sql += ';'
        
        return sql
    
    def batch_generate(
        self,
        questions: List[str],
        intents: List[str],
        farmer_ids: List[Optional[int]]
    ) -> List[Dict[str, Any]]:
        """Generate SQL for multiple questions"""
        results = []
        for question, intent, farmer_id in zip(questions, intents, farmer_ids):
            result = self.generate(question, intent, {}, farmer_id)
            results.append(result)
        return results

# Global instance
_sql_generator = None

def get_sql_generator() -> SQLGenerator:
    """Get singleton SQL generator instance"""
    global _sql_generator
    if _sql_generator is None:
        _sql_generator = SQLGenerator(model_type=os.getenv("SQL_MODEL_TYPE", "template"))
    return _sql_generator

def generate_sql(
    question: str,
    intent: str,
    entities: Dict[str, Any] = None,
    farmer_id: Optional[int] = None
) -> Dict[str, Any]:
    """Convenience function for SQL generation"""
    generator = get_sql_generator()
    return generator.generate(question, intent, entities or {}, farmer_id)
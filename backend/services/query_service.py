"""
Query processing service - Core orchestration for natural language queries
Handles intent classification, SQL generation, and response formatting
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional, Tuple
import logging
import time
import re
from datetime import datetime

from backend.models.query import QueryResult
from backend.services.farmer_service import FarmerService

logger = logging.getLogger(__name__)

class QueryService:
    """Main service for processing natural language queries"""
    
    def __init__(self):
        self.farmer_service = FarmerService()
        self._intent_classifier = None
        self._sql_generator = None
        
    def _get_intent_classifier(self):
        """Lazy load intent classifier"""
        if self._intent_classifier is None:
            try:
                from ai.intent_classifier.predict import IntentPredictor
                self._intent_classifier = IntentPredictor()
            except Exception as e:
                logger.error(f"Failed to load intent classifier: {e}")
                raise
        return self._intent_classifier
    
    def _get_sql_generator(self):
        """Lazy load SQL generator"""
        if self._sql_generator is None:
            try:
                from ai.sql_generator.generator import SQLGenerator
                self._sql_generator = SQLGenerator()
            except Exception as e:
                logger.error(f"Failed to load SQL generator: {e}")
                raise
        return self._sql_generator
    
    async def process_query(
        self,
        db: Session,
        question: str,
        phone_number: str,
        language: str = "hi"
    ) -> QueryResult:
        """
        Process a natural language query end-to-end
        
        Args:
            db: Database session
            question: Natural language question
            phone_number: Farmer's phone number
            language: Language code (hi, or, en)
        
        Returns:
            QueryResult with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Get farmer information
            farmer = self.farmer_service.get_farmer_by_phone(db, phone_number)
            if not farmer:
                return QueryResult(
                    answer=self._get_error_message("farmer_not_found", language),
                    intent="ERROR",
                    confidence=0,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error="Farmer not found"
                )
            
            # Step 2: Classify intent
            intent_result = await self._classify_intent(question, language)
            if not intent_result or intent_result.get("confidence", 0) < 0.5:
                return QueryResult(
                    answer=self._get_error_message("low_confidence", language),
                    intent="UNKNOWN",
                    confidence=intent_result.get("confidence", 0),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error="Low confidence in intent classification"
                )
            
            # Step 3: Generate SQL query
            sql_result = await self._generate_sql(
                question=question,
                intent=intent_result["intent"],
                entities=intent_result.get("entities", {}),
                farmer_id=farmer.farmer_id,
                language=language
            )
            
            if not sql_result.get("validated", False):
                return QueryResult(
                    answer=self._get_error_message("sql_generation_failed", language),
                    intent=intent_result["intent"],
                    confidence=intent_result["confidence"],
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error=f"SQL validation failed: {sql_result.get('errors', [])}"
                )
            
            # Step 4: Execute SQL query safely
            query_result = await self._execute_safely(db, sql_result["sql_query"])
            
            if not query_result["success"]:
                return QueryResult(
                    answer=self._get_error_message("query_execution_failed", language),
                    intent=intent_result["intent"],
                    confidence=intent_result["confidence"],
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error=query_result.get("error", "Query execution failed")
                )
            
            # Step 5: Format response
            formatted_response = await self._format_response(
                data=query_result["data"],
                intent=intent_result["intent"],
                question=question,
                language=language,
                farmer=farmer
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return QueryResult(
                answer=formatted_response["answer"],
                data=formatted_response.get("structured_data"),
                intent=intent_result["intent"],
                confidence=intent_result["confidence"],
                query_executed=sql_result["sql_query"],
                processing_time_ms=processing_time_ms,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return QueryResult(
                answer=self._get_error_message("general_error", language),
                intent="ERROR",
                confidence=0,
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error=str(e)
            )
    
    async def _classify_intent(self, question: str, language: str) -> Dict[str, Any]:
        """Classify the intent of the question"""
        try:
            predictor = self._get_intent_classifier()
            result = predictor.predict(question, language)
            return result
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            # Fallback to keyword-based classification
            return self._keyword_based_intent(question, language)
    
    def _keyword_based_intent(self, question: str, language: str) -> Dict[str, Any]:
        """Fallback intent classification using keywords"""
        question_lower = question.lower()
        
        # Payment keywords
        payment_keywords = ["pmkisan", "pm-kisan", "किश्त", "भुगतान", "पैसा", "kalia", "कलिया"]
        if any(kw in question_lower for kw in payment_keywords):
            return {"intent": "PAYMENT", "confidence": 0.7, "entities": {}}
        
        # Price keywords
        price_keywords = ["भाव", "मंडी", "दाम", "कीमत", "price", "mandi", "rate"]
        if any(kw in question_lower for kw in price_keywords):
            return {"intent": "PRICE", "confidence": 0.7, "entities": {}}
        
        # Soil keywords
        soil_keywords = ["मिट्टी", "soil", "खाद", "उर्वरक", "नाइट्रोजन", "phosphorus"]
        if any(kw in question_lower for kw in soil_keywords):
            return {"intent": "SOIL", "confidence": 0.7, "entities": {}}
        
        # Weather keywords
        weather_keywords = ["मौसम", "बारिश", "तापमान", "weather", "rain", "temperature"]
        if any(kw in question_lower for kw in weather_keywords):
            return {"intent": "WEATHER", "confidence": 0.7, "entities": {}}
        
        return {"intent": "UNKNOWN", "confidence": 0.3, "entities": {}}
    
    async def _generate_sql(
        self,
        question: str,
        intent: str,
        entities: Dict[str, Any],
        farmer_id: int,
        language: str
    ) -> Dict[str, Any]:
        """Generate SQL query from natural language"""
        try:
            generator = self._get_sql_generator()
            sql_result = generator.generate(
                question=question,
                intent=intent,
                entities=entities,
                farmer_id=farmer_id,
                language=language
            )
            return sql_result
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            # Return template-based SQL for common queries
            return self._template_based_sql(intent, farmer_id, entities)
    
    def _template_based_sql(self, intent: str, farmer_id: int, entities: Dict) -> Dict[str, Any]:
        """Fallback template-based SQL generation"""
        if intent == "PAYMENT":
            sql = f"""
                SELECT scheme_name, amount, payment_date, status
                FROM (
                    SELECT 'PM-KISAN' as scheme_name, amount, payment_date, status 
                    FROM pmkisan_payments WHERE farmer_id = {farmer_id}
                    UNION ALL
                    SELECT 'KALIA' as scheme_name, amount, payment_date, status 
                    FROM kalia_payments WHERE farmer_id = {farmer_id}
                ) payments
                ORDER BY payment_date DESC
                LIMIT 5
            """
        elif intent == "SOIL":
            sql = f"""
                SELECT nitrogen, phosphorus, potassium, ph, organic_carbon, 
                       test_date, recommendation
                FROM soil_health
                WHERE farmer_id = {farmer_id}
                ORDER BY test_date DESC
                LIMIT 1
            """
        elif intent == "PRICE":
            crop = entities.get("crop", "धान")
            sql = f"""
                SELECT crop, market, price, date
                FROM mandi_prices
                WHERE LOWER(crop) LIKE LOWER('%{crop}%')
                ORDER BY date DESC
                LIMIT 5
            """
        elif intent == "WEATHER":
            sql = """
                SELECT village, date, rainfall, temperature, forecast
                FROM weather
                WHERE date >= CURRENT_DATE
                ORDER BY date
                LIMIT 7
            """
        else:
            sql = "SELECT 'No data available' as message"
        
        return {
            "sql_query": sql,
            "validated": True,
            "confidence": 0.6,
            "errors": []
        }
    
    async def _execute_safely(self, db: Session, sql_query: str) -> Dict[str, Any]:
        """Execute SQL query with safety checks"""
        try:
            # Safety check - block non-SELECT queries
            sql_upper = sql_query.strip().upper()
            if not sql_upper.startswith("SELECT"):
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed",
                    "data": None
                }
            
            # Additional safety: block dangerous operations
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return {
                        "success": False,
                        "error": f"Dangerous operation '{keyword}' blocked",
                        "data": None
                    }
            
            # Execute query
            result = db.execute(text(sql_query))
            
            # Fetch results
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dicts
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "success": True,
                "data": data,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def _format_response(
        self,
        data: list,
        intent: str,
        question: str,
        language: str,
        farmer: Any
    ) -> Dict[str, Any]:
        """Format the query results into a natural language response"""
        
        if not data:
            return {
                "answer": self._get_error_message("no_data", language),
                "structured_data": None
            }
        
        if intent == "PAYMENT":
            return self._format_payment_response(data, language, farmer)
        elif intent == "PRICE":
            return self._format_price_response(data, language)
        elif intent == "SOIL":
            return self._format_soil_response(data, language)
        elif intent == "WEATHER":
            return self._format_weather_response(data, language)
        else:
            return {
                "answer": str(data[:3]) if data else "No data found",
                "structured_data": data[:5]
            }
    
    def _format_payment_response(self, data: list, language: str, farmer: Any) -> Dict[str, Any]:
        """Format payment data into response"""
        if language == "hi":
            if not data:
                return {"answer": "आपका कोई भुगतान अभी तक नहीं हुआ है।", "structured_data": None}
            
            total_amount = sum(float(row.get('amount', 0)) for row in data)
            latest = data[0]
            
            answer = f"नमस्ते {farmer.name} जी, "
            answer += f"आपको अब तक कुल ₹{total_amount:,.2f} का भुगतान मिल चुका है। "
            answer += f"आपका अंतिम भुगतान ₹{latest.get('amount', 0):,.2f} "
            answer += f"दिनांक {latest.get('payment_date', 'N/A')} को हुआ था।"
            
            return {"answer": answer, "structured_data": data[:3]}
        
        else:  # English fallback
            if not data:
                return {"answer": "No payments found for this farmer.", "structured_data": None}
            
            total_amount = sum(float(row.get('amount', 0)) for row in data)
            latest = data[0]
            
            answer = f"Dear {farmer.name}, "
            answer += f"Total payments received: ₹{total_amount:,.2f}. "
            answer += f"Latest payment: ₹{latest.get('amount', 0):,.2f} on {latest.get('payment_date', 'N/A')}."
            
            return {"answer": answer, "structured_data": data[:3]}
    
    def _format_price_response(self, data: list, language: str) -> Dict[str, Any]:
        """Format mandi price data into response"""
        if language == "hi":
            if not data:
                return {"answer": "इस समय मंडी भाव उपलब्ध नहीं है।", "structured_data": None}
            
            latest = data[0]
            answer = f"{latest.get('crop', '')} का भाव {latest.get('market', '')} मंडी में "
            answer += f"₹{latest.get('price', 0):,.2f} प्रति क्विंटल है।"
            
            return {"answer": answer, "structured_data": data[:5]}
        else:
            if not data:
                return {"answer": "Mandi prices not available at this time.", "structured_data": None}
            
            latest = data[0]
            answer = f"{latest.get('crop', '')} price in {latest.get('market', '')} mandi "
            answer += f"is ₹{latest.get('price', 0):,.2f} per quintal."
            
            return {"answer": answer, "structured_data": data[:5]}
    
    def _format_soil_response(self, data: list, language: str) -> Dict[str, Any]:
        """Format soil health data into response"""
        if language == "hi":
            if not data:
                return {"answer": "आपकी मिट्टी की रिपोर्ट उपलब्ध नहीं है।", "structured_data": None}
            
            report = data[0]
            answer = f"मिट्टी परीक्षण रिपोर्ट: "
            answer += f"नाइट्रोजन: {report.get('nitrogen', 'N/A')} kg/ha, "
            answer += f"फास्फोरस: {report.get('phosphorus', 'N/A')} kg/ha, "
            answer += f"पोटाश: {report.get('potassium', 'N/A')} kg/ha, "
            answer += f"पीएच मान: {report.get('ph', 'N/A')}. "
            
            if report.get('recommendation'):
                answer += f"सुझाव: {report['recommendation']}"
            
            return {"answer": answer, "structured_data": report}
        else:
            if not data:
                return {"answer": "Soil health report not available.", "structured_data": None}
            
            report = data[0]
            answer = f"Soil test report: "
            answer += f"Nitrogen: {report.get('nitrogen', 'N/A')} kg/ha, "
            answer += f"Phosphorus: {report.get('phosphorus', 'N/A')} kg/ha, "
            answer += f"Potassium: {report.get('potassium', 'N/A')} kg/ha, "
            answer += f"pH: {report.get('ph', 'N/A')}. "
            
            if report.get('recommendation'):
                answer += f"Recommendation: {report['recommendation']}"
            
            return {"answer": answer, "structured_data": report}
    
    def _format_weather_response(self, data: list, language: str) -> Dict[str, Any]:
        """Format weather data into response"""
        if language == "hi":
            if not data:
                return {"answer": "मौसम की जानकारी उपलब्ध नहीं है।", "structured_data": None}
            
            today = data[0] if data else None
            if today:
                answer = f"आज का मौसम: {today.get('forecast', '')}, "
                answer += f"तापमान: {today.get('temperature', 'N/A')}°C, "
                answer += f"वर्षा: {today.get('rainfall', 0)} मिमी।"
                
                if len(data) > 1:
                    answer += f" अगले कुछ दिनों में {data[1].get('forecast', '')} की संभावना है।"
                
                return {"answer": answer, "structured_data": data[:3]}
        
        return {"answer": str(data[:3]) if data else "No weather data available", "structured_data": data[:3]}
    
    def _get_error_message(self, error_type: str, language: str) -> str:
        """Get localized error messages"""
        messages = {
            "farmer_not_found": {
                "hi": "यह मोबाइल नंबर हमारे डेटाबेस में पंजीकृत नहीं है। कृपया सही नंबर डालें।",
                "or": "ଏହି ମୋବାଇଲ୍ ନମ୍ବର ଆମ ଡାଟାବେସରେ ପଞ୍ଜୀକୃତ ନୁହେଁ।",
                "en": "This mobile number is not registered in our database."
            },
            "low_confidence": {
                "hi": "मुझे आपका प्रश्न समझने में परेशानी हो रही है। कृपया सरल भाषा में पूछें।",
                "or": "ମୁଁ ଆପଣଙ୍କ ପ୍ରଶ୍ନ ବୁଝିବାରେ ଅସୁବିଧା ହେଉଛି।",
                "en": "I'm having trouble understanding your question. Please ask in simpler terms."
            },
            "no_data": {
                "hi": "आपके प्रश्न के लिए कोई डेटा उपलब्ध नहीं है।",
                "or": "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ପାଇଁ କୌଣସି ଡାଟା ଉପଲବ୍ଧ ନାହିଁ।",
                "en": "No data available for your query."
            },
            "general_error": {
                "hi": "क्षमा करें, कुछ तकनीकी समस्या आई है। कृपया बाद में पुनः प्रयास करें।",
                "or": "କ୍ଷମା କରନ୍ତୁ, କିଛି ଟେକ୍ନିକାଲ୍ ସମସ୍ୟା ହୋଇଛି।",
                "en": "Sorry, a technical issue occurred. Please try again later."
            },
            "sql_generation_failed": {
                "hi": "आपका प्रश्न समझ नहीं आया। कृपया स्पष्ट रूप से पूछें।",
                "or": "ଆପଣଙ୍କ ପ୍ରଶ୍ନ ବୁଝିପାରିଲି ନାହିଁ।",
                "en": "Could not understand your query. Please rephrase."
            },
            "query_execution_failed": {
                "hi": "डेटाबेस से जानकारी लाने में समस्या आई।",
                "or": "ଡାଟାବେସରୁ ସୂଚନା ଆଣିବାରେ ସମସ୍ୟା ହେଉଛି।",
                "en": "Problem fetching data from database."
            }
        }
        
        return messages.get(error_type, {}).get(language, messages.get(error_type, {}).get("en", "An error occurred."))

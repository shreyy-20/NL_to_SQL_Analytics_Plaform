"""
SQL Query Validator for Safety
Blocks dangerous operations and validates syntax
"""

import re
import logging
from typing import Dict, Any, List, Tuple
from sqlparse import parse, sql
from sqlparse.tokens import Keyword, DML, DDL

logger = logging.getLogger(__name__)

class SQLValidator:
    """Validate SQL queries for safety and correctness"""
    
    # Blocked SQL operations (unsafe)
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
        'CREATE', 'TRUNCATE', 'MERGE', 'REPLACE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL',
        'DECLARE', 'SET', 'INTO OUTFILE', 'INTO DUMPFILE',
        'LOAD_FILE', 'BENCHMARK', 'SLEEP'
    ]
    
    # Allowed operations
    ALLOWED_KEYWORDS = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN']
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r';\s*DROP\s+',
        r';\s*DELETE\s+',
        r';\s*UPDATE\s+',
        r';\s*INSERT\s+',
        r';\s*ALTER\s+',
        r'\bINFORMATION_SCHEMA\b',
        r'\bxp_cmdshell\b',
        r'\bexec\s+xp_',
        r'\bcert_encoded\b',
        r'\bPASSWORD\b',
        r'\bUSERS\b.*\bPASSWORD\b',
    ]
    
    # Table whitelist
    ALLOWED_TABLES = {
        'farmers', 'pmkisan_payments', 'kalia_payments', 
        'soil_health', 'mandi_prices', 'weather', 'query_logs'
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, sql_query: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety
        
        Args:
            sql_query: SQL query string to validate
        
        Returns:
            Dictionary with validation results
        """
        self.errors = []
        self.warnings = []
        
        # Basic checks
        self._check_empty(sql_query)
        self._check_query_type(sql_query)
        self._check_dangerous_keywords(sql_query)
        self._check_dangerous_patterns(sql_query)
        self._check_multiple_queries(sql_query)
        
        # Parse and analyze
        parsed = self._parse_sql(sql_query)
        if parsed:
            self._analyze_parsed_query(parsed)
            self._check_table_whitelist(parsed)
            self._check_where_clause(parsed)
        
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "query_type": self._get_query_type(sql_query),
            "tables_accessed": self._extract_tables(sql_query)
        }
    
    def _check_empty(self, sql_query: str):
        """Check if query is empty"""
        if not sql_query or not sql_query.strip():
            self.errors.append("Empty SQL query")
    
    def _check_query_type(self, sql_query: str):
        """Check if query type is allowed"""
        sql_upper = sql_query.strip().upper()
        
        # Check if starts with allowed keyword
        allowed = False
        for keyword in self.ALLOWED_KEYWORDS:
            if sql_upper.startswith(keyword):
                allowed = True
                break
        
        if not allowed:
            self.errors.append(
                f"Query must start with one of: {', '.join(self.ALLOWED_KEYWORDS)}"
            )
    
    def _check_dangerous_keywords(self, sql_query: str):
        """Check for dangerous keywords"""
        sql_upper = sql_query.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            # Use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sql_upper):
                self.errors.append(f"Dangerous keyword '{keyword}' detected")
    
    def _check_dangerous_patterns(self, sql_query: str):
        """Check for dangerous SQL patterns"""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_query, re.IGNORECASE):
                self.errors.append(f"Dangerous pattern detected: {pattern}")
    
    def _check_multiple_queries(self, sql_query: str):
        """Check for multiple queries separated by semicolons"""
        # Remove comments first
        cleaned = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        # Count semicolons outside string literals
        # Simplified check
        if cleaned.count(';') > 1:
            self.warnings.append("Multiple queries detected, only first will be executed")
    
    def _parse_sql(self, sql_query: str):
        """Parse SQL using sqlparse"""
        try:
            parsed = parse(sql_query)
            return parsed[0] if parsed else None
        except Exception as e:
            self.warnings.append(f"Could not fully parse SQL: {e}")
            return None
    
    def _analyze_parsed_query(self, parsed):
        """Analyze parsed SQL statement"""
        try:
            # Check for SELECT *
            if self._has_select_star(parsed):
                self.warnings.append("Using SELECT * is inefficient, consider specifying columns")
            
            # Check for missing LIMIT
            if not self._has_limit_clause(parsed):
                self.warnings.append("No LIMIT clause - consider adding one for performance")
            
        except Exception as e:
            logger.debug(f"Error in analysis: {e}")
    
    def _has_select_star(self, parsed) -> bool:
        """Check if query has SELECT *"""
        flattened = str(parsed).lower()
        return re.search(r'select\s+\*\s+from', flattened) is not None
    
    def _has_limit_clause(self, parsed) -> bool:
        """Check if query has LIMIT clause"""
        sql_lower = str(parsed).lower()
        return ' limit ' in sql_lower or sql_lower.endswith(' limit')
    
    def _check_table_whitelist(self, parsed):
        """Check that only allowed tables are accessed"""
        sql_text = str(parsed) if parsed is not None else ''
        tables = self._extract_tables(sql_text)
        
        for table in tables:
            if table not in self.ALLOWED_TABLES:
                self.errors.append(f"Access to table '{table}' is not allowed")
    
    def _extract_tables_from_parsed(self, parsed) -> List[str]:
        """Extract table names from parsed SQL"""
        tables = []
        try:
            from sqlparse.sql import Identifier, Where, Comparison, Parenthesis
            from sqlparse.tokens import Name, Keyword
            
            def extract_from_tokens(token_list):
                for token in token_list:
                    if token.is_group:
                        extract_from_tokens(token.tokens)
                    elif isinstance(token, Identifier):
                        # Extract table name from identifier
                        table_name = str(token).split()[0].lower()
                        if table_name not in tables and table_name not in ['as', 'on']:
                            tables.append(table_name)
                    elif token.ttype is Name and token.value.lower() not in ['select', 'from', 'where', 'and', 'or']:
                        # Potential table name
                        if token.value.lower() not in tables:
                            tables.append(token.value.lower())
            
            extract_from_tokens(parsed.tokens)
        except Exception as e:
            logger.debug(f"Table extraction failed: {e}")
        
        return tables
    
    def _check_where_clause(self, parsed):
        """Check if WHERE clause exists for potentially expensive queries"""
        sql_lower = str(parsed).lower()
        
        # Only warn for tables that might be large
        large_tables = ['pmkisan_payments', 'kalia_payments', 'mandi_prices']
        
        for table in large_tables:
            if table in sql_lower and ' where ' not in sql_lower:
                self.warnings.append(f"Query on '{table}' without WHERE clause may be slow")
    
    def _get_query_type(self, sql_query: str) -> str:
        """Determine the type of query"""
        sql_upper = sql_query.strip().upper()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('SHOW'):
            return 'SHOW'
        elif sql_upper.startswith('DESCRIBE'):
            return 'DESCRIBE'
        elif sql_upper.startswith('EXPLAIN'):
            return 'EXPLAIN'
        else:
            return 'UNKNOWN'
    
    def _extract_tables(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        tables = []
        
        # Simple regex-based extraction for tables after FROM/JOIN
        patterns = [
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql_query, re.IGNORECASE)
            tables.extend([m.lower() for m in matches])
        
        # Remove duplicates
        return list(set(tables))
    
    def sanitize(self, sql_query: str) -> str:
        """Attempt to sanitize SQL query (remove dangerous parts)"""
        # Remove comments
        sanitized = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Add LIMIT if missing
        if 'limit' not in sanitized.lower() and sanitized.lower().startswith('select'):
            # Add LIMIT after WHERE clause or at end
            if 'where' in sanitized.lower():
                sanitized = re.sub(
                    r'(where\s+.*?)(;?\s*$)',
                    r'\1 LIMIT 100;',
                    sanitized,
                    flags=re.IGNORECASE
                )
            else:
                sanitized = re.sub(r'(from\s+.*?)(;?\s*$)', r'\1 LIMIT 100;', sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Convenience functions
def validate_sql(sql_query: str) -> Dict[str, Any]:
    """Quick validation of SQL query"""
    validator = SQLValidator()
    return validator.validate(sql_query)

def is_safe_sql(sql_query: str) -> bool:
    """Check if SQL query is safe to execute"""
    result = validate_sql(sql_query)
    return result["is_valid"]

def sanitize_sql(sql_query: str) -> str:
    """Sanitize SQL query"""
    validator = SQLValidator()
    return validator.sanitize(sql_query)
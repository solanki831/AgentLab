"""
✅ VALIDATION AGENT (Reviewer)
Specialized agent for test assertions and data validation

Responsibilities:
- Schema validation
- Data assertions
- Response validation
- Cross-test validation
- Data integrity checks
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    Reviewer - Data validation and assertion specialist
    High-speed validation of test results and data integrity
    """
    
    def __init__(self):
        self.agent_type = "validation"
        self.capabilities = [
            "schema_validation",
            "data_assertions",
            "json_validation",
            "xml_validation",
            "regex_validation",
            "type_checking",
            "range_validation",
            "cross_test_validation",
            "data_integrity_check"
        ]
        self.validation_cache = {}
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute validation checks
        
        Args:
            target: Data or result to validate
            config: Validation rules and assertions
        
        Returns:
            Validation result with pass/fail details
        """
        logger.info(f"✅ Validation Agent: Validating {target}")
        start_time = datetime.now()
        
        try:
            data = config.get("data")
            validations = config.get("validations", [])
            
            # Execute all validations
            validation_results = await self._run_validations(data, validations)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": validation_results["all_passed"],
                "agent": "Validation Agent",
                "target": target,
                "total_validations": validation_results["total"],
                "passed": validation_results["passed"],
                "failed": validation_results["failed"],
                "results": validation_results["results"],
                "execution_time": execution_time,
                "data_integrity_score": validation_results["integrity_score"]
            }
        
        except Exception as e:
            logger.error(f"❌ Validation Agent error: {e}")
            return {
                "success": False,
                "agent": "Validation Agent",
                "target": target,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _run_validations(
        self,
        data: Any,
        validations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run all validation checks"""
        
        results = {
            "all_passed": True,
            "total": len(validations),
            "passed": 0,
            "failed": 0,
            "results": [],
            "integrity_score": 1.0
        }
        
        if not validations:
            # Return success if no validations specified
            return results
        
        for validation in validations:
            validation_type = validation.get("type")
            
            try:
                if validation_type == "equals":
                    result = self._validate_equals(data, validation)
                elif validation_type == "contains":
                    result = self._validate_contains(data, validation)
                elif validation_type == "regex":
                    result = self._validate_regex(data, validation)
                elif validation_type == "schema":
                    result = self._validate_schema(data, validation)
                elif validation_type == "type":
                    result = self._validate_type(data, validation)
                elif validation_type == "range":
                    result = self._validate_range(data, validation)
                elif validation_type == "json_path":
                    result = self._validate_json_path(data, validation)
                elif validation_type == "length":
                    result = self._validate_length(data, validation)
                elif validation_type == "unique":
                    result = self._validate_unique(data, validation)
                elif validation_type == "not_null":
                    result = self._validate_not_null(data, validation)
                else:
                    result = {
                        "passed": False,
                        "type": validation_type,
                        "error": f"Unknown validation type: {validation_type}"
                    }
                
                results["results"].append(result)
                
                if result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["all_passed"] = False
            
            except Exception as e:
                results["failed"] += 1
                results["all_passed"] = False
                results["results"].append({
                    "passed": False,
                    "type": validation_type,
                    "error": str(e)
                })
        
        # Calculate integrity score
        results["integrity_score"] = results["passed"] / results["total"] if results["total"] > 0 else 1.0
        
        return results
    
    def _validate_equals(self, data: Any, validation: Dict) -> Dict:
        """Validate exact equality"""
        field = validation.get("field")
        expected = validation.get("expected")
        
        actual = self._get_field_value(data, field) if field else data
        passed = actual == expected
        
        return {
            "type": "equals",
            "passed": passed,
            "field": field,
            "expected": expected,
            "actual": actual
        }
    
    def _validate_contains(self, data: Any, validation: Dict) -> Dict:
        """Validate contains (substring or element)"""
        field = validation.get("field")
        expected = validation.get("expected")
        
        actual = self._get_field_value(data, field) if field else data
        
        if isinstance(actual, str):
            passed = expected in actual
        elif isinstance(actual, (list, tuple)):
            passed = expected in actual
        elif isinstance(actual, dict):
            passed = expected in actual.values()
        else:
            passed = False
        
        return {
            "type": "contains",
            "passed": passed,
            "field": field,
            "expected": expected,
            "actual": actual
        }
    
    def _validate_regex(self, data: Any, validation: Dict) -> Dict:
        """Validate regex pattern"""
        field = validation.get("field")
        pattern = validation.get("pattern")
        
        actual = self._get_field_value(data, field) if field else data
        
        if not isinstance(actual, str):
            actual = str(actual)
        
        passed = bool(re.match(pattern, actual))
        
        return {
            "type": "regex",
            "passed": passed,
            "field": field,
            "pattern": pattern,
            "actual": actual
        }
    
    def _validate_schema(self, data: Any, validation: Dict) -> Dict:
        """Validate JSON schema"""
        schema = validation.get("schema")
        
        passed = self._check_schema(data, schema)
        
        return {
            "type": "schema",
            "passed": passed,
            "schema": schema,
            "data": data
        }
    
    def _validate_type(self, data: Any, validation: Dict) -> Dict:
        """Validate data type"""
        field = validation.get("field")
        expected_type = validation.get("expected_type")
        
        actual = self._get_field_value(data, field) if field else data
        
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "float": float,
            "boolean": bool,
            "object": dict,
            "array": list,
            "null": type(None)
        }
        
        expected_py_type = type_map.get(expected_type)
        passed = isinstance(actual, expected_py_type) if expected_py_type else False
        
        return {
            "type": "type",
            "passed": passed,
            "field": field,
            "expected_type": expected_type,
            "actual_type": type(actual).__name__
        }
    
    def _validate_range(self, data: Any, validation: Dict) -> Dict:
        """Validate numeric range"""
        field = validation.get("field")
        min_val = validation.get("min")
        max_val = validation.get("max")
        
        actual = self._get_field_value(data, field) if field else data
        
        passed = True
        if min_val is not None and actual < min_val:
            passed = False
        if max_val is not None and actual > max_val:
            passed = False
        
        return {
            "type": "range",
            "passed": passed,
            "field": field,
            "min": min_val,
            "max": max_val,
            "actual": actual
        }
    
    def _validate_json_path(self, data: Any, validation: Dict) -> Dict:
        """Validate JSON path exists and optionally equals expected value"""
        path = validation.get("path")
        expected = validation.get("expected")
        
        actual = self._get_json_path(data, path)
        
        if expected is not None:
            passed = actual == expected
        else:
            passed = actual is not None
        
        return {
            "type": "json_path",
            "passed": passed,
            "path": path,
            "expected": expected,
            "actual": actual
        }
    
    def _validate_length(self, data: Any, validation: Dict) -> Dict:
        """Validate length of string/array"""
        field = validation.get("field")
        min_length = validation.get("min")
        max_length = validation.get("max")
        exact_length = validation.get("exact")
        
        actual = self._get_field_value(data, field) if field else data
        actual_length = len(actual) if hasattr(actual, "__len__") else 0
        
        passed = True
        if exact_length is not None:
            passed = actual_length == exact_length
        else:
            if min_length is not None and actual_length < min_length:
                passed = False
            if max_length is not None and actual_length > max_length:
                passed = False
        
        return {
            "type": "length",
            "passed": passed,
            "field": field,
            "min": min_length,
            "max": max_length,
            "exact": exact_length,
            "actual": actual_length
        }
    
    def _validate_unique(self, data: Any, validation: Dict) -> Dict:
        """Validate array has unique elements"""
        field = validation.get("field")
        
        actual = self._get_field_value(data, field) if field else data
        
        if not isinstance(actual, (list, tuple)):
            passed = False
        else:
            passed = len(actual) == len(set(actual))
        
        return {
            "type": "unique",
            "passed": passed,
            "field": field,
            "duplicates": len(actual) - len(set(actual)) if isinstance(actual, (list, tuple)) else 0
        }
    
    def _validate_not_null(self, data: Any, validation: Dict) -> Dict:
        """Validate value is not null/None"""
        field = validation.get("field")
        
        actual = self._get_field_value(data, field) if field else data
        passed = actual is not None
        
        return {
            "type": "not_null",
            "passed": passed,
            "field": field,
            "actual": actual
        }
    
    def _get_field_value(self, data: Any, field: str) -> Any:
        """Get field value from data (supports dot notation)"""
        if not field:
            return data
        
        return self._get_json_path(data, field)
    
    def _get_json_path(self, data: Any, path: str) -> Any:
        """Extract value from JSON using path notation"""
        if not path:
            return data
        
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                return None
            
            if current is None:
                break
        
        return current
    
    def _check_schema(self, data: Any, schema: Dict) -> bool:
        """Check data against schema (simplified JSON schema)"""
        if not isinstance(data, dict):
            return False
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False
        
        # Check properties
        properties = schema.get("properties", {})
        for field, spec in properties.items():
            if field in data:
                value = data[field]
                expected_type = spec.get("type")
                
                type_map = {
                    "string": str,
                    "number": (int, float),
                    "integer": int,
                    "boolean": bool,
                    "object": dict,
                    "array": list
                }
                
                py_type = type_map.get(expected_type)
                if py_type and not isinstance(value, py_type):
                    return False
        
        return True
    
    async def batch_validate(
        self,
        items: List[Dict[str, Any]],
        validation_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate multiple items in batch"""
        logger.info(f"✅ Validation Agent: Batch validating {len(items)} items")
        
        results = []
        for idx, item in enumerate(items):
            config = {
                "data": item,
                "validations": validation_rules
            }
            result = await self.execute(f"item_{idx}", config)
            results.append(result)
        
        all_passed = all(r.get("success") for r in results)
        total_validations = sum(r.get("total_validations", 0) for r in results)
        total_passed = sum(r.get("passed", 0) for r in results)
        
        return {
            "success": all_passed,
            "total_items": len(items),
            "items_passed": sum(1 for r in results if r.get("success")),
            "total_validations": total_validations,
            "total_passed": total_passed,
            "total_failed": total_validations - total_passed,
            "results": results
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Return agent status"""
        return {
            "agent_type": self.agent_type,
            "name": "Validation Agent",
            "role": "Reviewer",
            "capabilities": self.capabilities,
            "is_available": True,
            "cache_size": len(self.validation_cache)
        }

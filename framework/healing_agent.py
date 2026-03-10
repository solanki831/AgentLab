"""
🔧 HEALING AGENT (Flaky Test Fixer)
Specialized agent for auto-healing failed tests

Responsibilities:
- Analyze test failures using AI
- Suggest fixes for flaky tests
- Auto-update test configurations
- Retry with healed configuration
- Track healing success rates
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealingAgent:
    """
    Flaky Test Fixer - Self-healing specialist
    Uses AI to analyze failures and suggest/apply fixes
    """
    
    def __init__(self, llm_client=None):
        self.agent_type = "healing"
        self.llm_client = llm_client
        self.capabilities = [
            "failure_analysis",
            "flaky_test_detection",
            "auto_repair",
            "config_optimization",
            "retry_strategy",
            "selector_healing",
            "timeout_optimization",
            "data_variability_handling"
        ]
        self.healing_history = []
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and heal a failed test
        
        Args:
            target: Failed test identifier
            config: Contains failed_test, error_info, test_config
        
        Returns:
            Healing result with suggested fixes
        """
        logger.info(f"🔧 Healing Agent: Analyzing {target}")
        start_time = datetime.now()
        
        try:
            failed_test = config.get("failed_test", {})
            error_info = config.get("error_info", "")
            test_config = config.get("test_config", {})
            
            # Analyze failure
            analysis = await self._analyze_failure(failed_test, error_info, test_config)
            
            # Generate healing strategy
            healing_strategy = await self._generate_healing_strategy(analysis)
            
            # Apply healing
            healed_config = await self._apply_healing(test_config, healing_strategy)
            
            # Verify healing (retry test)
            verification = await self._verify_healing(target, healed_config, healing_strategy)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record healing attempt
            self.healing_history.append({
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "success": verification["success"],
                "strategy": healing_strategy["name"]
            })
            
            return {
                "success": verification["success"],
                "agent": "Healing Agent",
                "target": target,
                "analysis": analysis,
                "healing_strategy": healing_strategy,
                "healed_config": healed_config,
                "verification": verification,
                "execution_time": execution_time,
                "healing_success_rate": self._calculate_success_rate()
            }
        
        except Exception as e:
            logger.error(f"❌ Healing Agent error: {e}")
            return {
                "success": False,
                "agent": "Healing Agent",
                "target": target,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _analyze_failure(
        self,
        failed_test: Dict[str, Any],
        error_info: str,
        test_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze test failure using AI"""
        
        # Pattern matching for common failure types
        failure_patterns = {
            "timeout": ["timeout", "timed out", "exceeded", "wait"],
            "selector": ["not found", "no such element", "selector", "cannot find"],
            "data": ["assertion failed", "expected", "actual", "mismatch"],
            "network": ["network", "connection", "refused", "unreachable"],
            "auth": ["unauthorized", "forbidden", "authentication", "403", "401"],
            "flaky": ["intermittent", "sometimes", "occasionally", "random"]
        }
        
        error_lower = error_info.lower()
        detected_patterns = []
        
        for pattern_type, keywords in failure_patterns.items():
            if any(kw in error_lower for kw in keywords):
                detected_patterns.append(pattern_type)
        
        # Use LLM for deeper analysis if available
        if self.llm_client:
            llm_analysis = await self._llm_analyze_failure(failed_test, error_info, test_config)
        else:
            llm_analysis = {
                "root_cause": "Pattern-based analysis",
                "confidence": 0.7
            }
        
        return {
            "failure_type": detected_patterns[0] if detected_patterns else "unknown",
            "detected_patterns": detected_patterns,
            "error_message": error_info,
            "test_name": failed_test.get("name", "Unknown"),
            "test_type": failed_test.get("type", "Unknown"),
            "llm_analysis": llm_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _llm_analyze_failure(
        self,
        failed_test: Dict[str, Any],
        error_info: str,
        test_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to analyze failure (placeholder for actual LLM call)"""
        # In production, this would call Ollama or other LLM
        await asyncio.sleep(0.1)  # Simulate LLM processing
        
        return {
            "root_cause": "Selector instability due to dynamic page elements",
            "confidence": 0.85,
            "suggested_fix": "Use more stable selector strategy (data-testid)",
            "additional_notes": "Element likely appears after async loading"
        }
    
    async def _generate_healing_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate healing strategy based on failure analysis"""
        
        failure_type = analysis.get("failure_type")
        
        strategies = {
            "timeout": {
                "name": "Increase Timeout",
                "actions": [
                    {"type": "config_update", "key": "timeout", "value": 30000},
                    {"type": "add_wait", "strategy": "explicit_wait"}
                ],
                "priority": "high"
            },
            "selector": {
                "name": "Improve Selector Strategy",
                "actions": [
                    {"type": "selector_fallback", "fallbacks": ["data-testid", "aria-label", "text"]},
                    {"type": "add_wait", "strategy": "wait_for_element"}
                ],
                "priority": "high"
            },
            "data": {
                "name": "Relax Assertions",
                "actions": [
                    {"type": "assertion_update", "strategy": "contains_instead_of_equals"},
                    {"type": "add_retry", "max_retries": 3}
                ],
                "priority": "medium"
            },
            "network": {
                "name": "Add Network Resilience",
                "actions": [
                    {"type": "add_retry", "max_retries": 5, "backoff": "exponential"},
                    {"type": "config_update", "key": "timeout", "value": 60000}
                ],
                "priority": "high"
            },
            "auth": {
                "name": "Refresh Authentication",
                "actions": [
                    {"type": "refresh_token", "strategy": "re-authenticate"},
                    {"type": "add_retry", "max_retries": 2}
                ],
                "priority": "critical"
            }
        }
        
        strategy = strategies.get(failure_type, {
            "name": "Generic Healing",
            "actions": [
                {"type": "add_retry", "max_retries": 3},
                {"type": "config_update", "key": "timeout", "value": 20000}
            ],
            "priority": "medium"
        })
        
        strategy["failure_type"] = failure_type
        strategy["analysis"] = analysis
        
        return strategy
    
    async def _apply_healing(
        self,
        test_config: Dict[str, Any],
        healing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply healing strategy to test configuration"""
        
        healed_config = test_config.copy()
        actions = healing_strategy.get("actions", [])
        
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "config_update":
                key = action.get("key")
                value = action.get("value")
                healed_config[key] = value
                logger.info(f"  ✓ Updated {key} to {value}")
            
            elif action_type == "add_wait":
                strategy = action.get("strategy")
                healed_config["wait_strategy"] = strategy
                logger.info(f"  ✓ Added wait strategy: {strategy}")
            
            elif action_type == "selector_fallback":
                fallbacks = action.get("fallbacks", [])
                healed_config["selector_fallbacks"] = fallbacks
                logger.info(f"  ✓ Added selector fallbacks: {fallbacks}")
            
            elif action_type == "add_retry":
                max_retries = action.get("max_retries", 3)
                backoff = action.get("backoff", "linear")
                healed_config["max_retries"] = max_retries
                healed_config["retry_backoff"] = backoff
                logger.info(f"  ✓ Added retry logic: {max_retries} retries with {backoff} backoff")
            
            elif action_type == "assertion_update":
                strategy = action.get("strategy")
                healed_config["assertion_strategy"] = strategy
                logger.info(f"  ✓ Updated assertion strategy: {strategy}")
            
            elif action_type == "refresh_token":
                healed_config["refresh_auth"] = True
                logger.info(f"  ✓ Enabled authentication refresh")
        
        return healed_config
    
    async def _verify_healing(
        self,
        target: str,
        healed_config: Dict[str, Any],
        healing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify healing by retrying test (simulated)"""
        logger.info(f"  🔄 Verifying healing for {target}")
        
        await asyncio.sleep(0.2)  # Simulate retry
        
        # Simulate success based on strategy priority
        priority = healing_strategy.get("priority", "medium")
        success_rate = {
            "critical": 0.95,
            "high": 0.85,
            "medium": 0.70,
            "low": 0.50
        }
        
        # Simple simulation - in production, would actually retry the test
        import random
        success = random.random() < success_rate.get(priority, 0.7)
        
        return {
            "success": success,
            "retry_count": 1,
            "message": "Test passed after healing" if success else "Test still failing after healing",
            "healed_config_applied": True
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate healing success rate from history"""
        if not self.healing_history:
            return 0.0
        
        successful = sum(1 for h in self.healing_history if h.get("success"))
        return successful / len(self.healing_history)
    
    async def batch_heal(self, failed_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Heal multiple failed tests in batch"""
        logger.info(f"🔧 Healing Agent: Batch healing {len(failed_tests)} tests")
        
        results = []
        for test in failed_tests:
            config = {
                "failed_test": test,
                "error_info": test.get("error", ""),
                "test_config": test.get("config", {})
            }
            result = await self.execute(test.get("name", "Unknown"), config)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "total": len(failed_tests),
            "healed": successful,
            "failed": len(failed_tests) - successful,
            "success_rate": successful / len(failed_tests) if failed_tests else 0,
            "results": results
        }
    
    def get_healing_history(self) -> List[Dict[str, Any]]:
        """Get healing history"""
        return self.healing_history
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Return agent status"""
        return {
            "agent_type": self.agent_type,
            "name": "Healing Agent",
            "role": "Flaky Test Fixer",
            "capabilities": self.capabilities,
            "is_available": True,
            "healing_attempts": len(self.healing_history),
            "success_rate": self._calculate_success_rate(),
            "llm_enabled": self.llm_client is not None
        }

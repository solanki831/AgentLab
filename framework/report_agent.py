"""
📊 REPORT AGENT (Analyst)
Specialized agent for test reporting and root cause analysis

Responsibilities:
- Aggregate test results
- Generate comprehensive reports
- Root cause analysis (RCA)
- Trend analysis
- Metrics calculation
- Report formatting (HTML, JSON, Markdown)
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ReportAgent:
    """
    Analyst - Reporting and analysis specialist
    Generates comprehensive reports and performs RCA
    """
    
    def __init__(self):
        self.agent_type = "report"
        self.capabilities = [
            "result_aggregation",
            "report_generation",
            "root_cause_analysis",
            "trend_analysis",
            "metrics_calculation",
            "html_report",
            "json_report",
            "markdown_report",
            "executive_summary"
        ]
        self.report_history = []
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate report from test results
        
        Args:
            target: Report identifier
            config: Contains results, report_type, options
        
        Returns:
            Report with analysis and formatted output
        """
        logger.info(f"📊 Report Agent: Generating report {target}")
        start_time = datetime.now()
        
        try:
            results = config.get("results", [])
            report_type = config.get("report_type", "summary")
            options = config.get("options", {})
            
            # Aggregate results
            aggregated = await self._aggregate_results(results)
            
            # Calculate metrics
            metrics = await self._calculate_metrics(aggregated, results)
            
            # Perform RCA if there are failures
            rca = await self._root_cause_analysis(results) if aggregated["failed"] > 0 else {}
            
            # Generate report
            report = await self._generate_report(
                report_type,
                aggregated,
                metrics,
                rca,
                options
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store report in history
            self.report_history.append({
                "timestamp": datetime.now().isoformat(),
                "report_type": report_type,
                "total_tests": aggregated["total"],
                "passed": aggregated["passed"],
                "failed": aggregated["failed"]
            })
            
            return {
                "success": True,
                "agent": "Report Agent",
                "target": target,
                "report_type": report_type,
                "aggregated": aggregated,
                "metrics": metrics,
                "rca": rca,
                "report": report,
                "execution_time": execution_time
            }
        
        except Exception as e:
            logger.error(f"❌ Report Agent error: {e}")
            return {
                "success": False,
                "agent": "Report Agent",
                "target": target,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate test results"""
        
        aggregated = {
            "total": len(results),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "healed": 0,
            "by_agent": defaultdict(lambda: {"passed": 0, "failed": 0}),
            "by_type": defaultdict(lambda: {"passed": 0, "failed": 0}),
            "execution_time": 0
        }
        
        for result in results:
            success = result.get("success", False)
            agent = result.get("agent", "Unknown")
            test_type = result.get("type", "Unknown")
            
            if success:
                aggregated["passed"] += 1
                aggregated["by_agent"][agent]["passed"] += 1
                aggregated["by_type"][test_type]["passed"] += 1
            else:
                aggregated["failed"] += 1
                aggregated["by_agent"][agent]["failed"] += 1
                aggregated["by_type"][test_type]["failed"] += 1
            
            if result.get("healed"):
                aggregated["healed"] += 1
            
            aggregated["execution_time"] += result.get("execution_time", 0)
        
        # Convert defaultdicts to regular dicts
        aggregated["by_agent"] = dict(aggregated["by_agent"])
        aggregated["by_type"] = dict(aggregated["by_type"])
        
        return aggregated
    
    async def _calculate_metrics(
        self,
        aggregated: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate test metrics"""
        
        total = aggregated["total"]
        passed = aggregated["passed"]
        failed = aggregated["failed"]
        
        metrics = {
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "fail_rate": (failed / total * 100) if total > 0 else 0,
            "healing_rate": (aggregated["healed"] / failed * 100) if failed > 0 else 0,
            "avg_execution_time": aggregated["execution_time"] / total if total > 0 else 0,
            "total_execution_time": aggregated["execution_time"],
            "tests_per_second": total / aggregated["execution_time"] if aggregated["execution_time"] > 0 else 0
        }
        
        # Calculate response times for API tests
        api_results = [r for r in results if "response_time" in r]
        if api_results:
            response_times = [r["response_time"] for r in api_results]
            metrics["avg_response_time"] = sum(response_times) / len(response_times)
            metrics["min_response_time"] = min(response_times)
            metrics["max_response_time"] = max(response_times)
        
        # Calculate agent performance
        agent_performance = {}
        for agent, stats in aggregated["by_agent"].items():
            total_agent = stats["passed"] + stats["failed"]
            agent_performance[agent] = {
                "total": total_agent,
                "pass_rate": (stats["passed"] / total_agent * 100) if total_agent > 0 else 0
            }
        metrics["agent_performance"] = agent_performance
        
        return metrics
    
    async def _root_cause_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform root cause analysis on failures"""
        
        failures = [r for r in results if not r.get("success")]
        
        if not failures:
            return {}
        
        # Categorize failures
        failure_categories = defaultdict(list)
        error_patterns = defaultdict(int)
        
        for failure in failures:
            error = failure.get("error", "Unknown error")
            agent = failure.get("agent", "Unknown")
            
            # Pattern detection
            if "timeout" in error.lower():
                failure_categories["timeout"].append(failure)
                error_patterns["timeout"] += 1
            elif "not found" in error.lower() or "selector" in error.lower():
                failure_categories["selector"].append(failure)
                error_patterns["selector"] += 1
            elif "network" in error.lower() or "connection" in error.lower():
                failure_categories["network"].append(failure)
                error_patterns["network"] += 1
            elif "assertion" in error.lower() or "expected" in error.lower():
                failure_categories["assertion"].append(failure)
                error_patterns["assertion"] += 1
            else:
                failure_categories["other"].append(failure)
                error_patterns["other"] += 1
        
        # Identify top root causes
        sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
        top_root_causes = [
            {
                "category": category,
                "count": count,
                "percentage": (count / len(failures) * 100),
                "sample_errors": [f.get("error", "")[:100] for f in failure_categories[category][:3]]
            }
            for category, count in sorted_patterns[:5]
        ]
        
        # Recommendations
        recommendations = []
        for cause in top_root_causes:
            category = cause["category"]
            if category == "timeout":
                recommendations.append("Consider increasing timeout values or optimizing page load times")
            elif category == "selector":
                recommendations.append("Use more stable selectors (data-testid, aria-label)")
            elif category == "network":
                recommendations.append("Add retry logic and improve network resilience")
            elif category == "assertion":
                recommendations.append("Review assertion logic and expected values")
        
        return {
            "total_failures": len(failures),
            "failure_categories": dict(failure_categories),
            "top_root_causes": top_root_causes,
            "recommendations": recommendations,
            "failure_rate_by_agent": self._calculate_failure_rate_by_agent(failures)
        }
    
    def _calculate_failure_rate_by_agent(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate failure rate by agent"""
        by_agent = defaultdict(int)
        
        for failure in failures:
            agent = failure.get("agent", "Unknown")
            by_agent[agent] += 1
        
        return dict(by_agent)
    
    async def _generate_report(
        self,
        report_type: str,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any],
        rca: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate formatted report"""
        
        if report_type == "summary":
            return self._generate_summary_report(aggregated, metrics)
        elif report_type == "detailed":
            return self._generate_detailed_report(aggregated, metrics, rca)
        elif report_type == "executive":
            return self._generate_executive_report(aggregated, metrics)
        elif report_type == "html":
            return self._generate_html_report(aggregated, metrics, rca)
        elif report_type == "markdown":
            return self._generate_markdown_report(aggregated, metrics, rca)
        else:
            return self._generate_summary_report(aggregated, metrics)
    
    def _generate_summary_report(
        self,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary report"""
        return {
            "type": "summary",
            "summary": f"Executed {aggregated['total']} tests: {aggregated['passed']} passed, {aggregated['failed']} failed",
            "pass_rate": f"{metrics['pass_rate']:.1f}%",
            "execution_time": f"{aggregated['execution_time']:.2f}s",
            "avg_time_per_test": f"{metrics['avg_execution_time']:.2f}s"
        }
    
    def _generate_detailed_report(
        self,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any],
        rca: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed report"""
        return {
            "type": "detailed",
            "aggregated": aggregated,
            "metrics": metrics,
            "root_cause_analysis": rca,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_executive_report(
        self,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary"""
        status = "✅ PASSED" if aggregated["failed"] == 0 else "❌ FAILED"
        
        return {
            "type": "executive",
            "status": status,
            "headline": f"Test Suite: {aggregated['passed']}/{aggregated['total']} tests passed ({metrics['pass_rate']:.1f}%)",
            "key_metrics": {
                "Pass Rate": f"{metrics['pass_rate']:.1f}%",
                "Total Execution Time": f"{aggregated['execution_time']:.2f}s",
                "Tests Per Second": f"{metrics['tests_per_second']:.2f}"
            },
            "health_score": self._calculate_health_score(metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_markdown_report(
        self,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any],
        rca: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate markdown report"""
        
        md = f"""# Test Report
        
## Summary
- **Total Tests**: {aggregated['total']}
- **Passed**: {aggregated['passed']} ✅
- **Failed**: {aggregated['failed']} ❌
- **Pass Rate**: {metrics['pass_rate']:.1f}%

## Metrics
- **Execution Time**: {aggregated['execution_time']:.2f}s
- **Avg Time per Test**: {metrics['avg_execution_time']:.2f}s
- **Tests per Second**: {metrics['tests_per_second']:.2f}

## Results by Agent
"""
        
        for agent, stats in aggregated["by_agent"].items():
            total = stats["passed"] + stats["failed"]
            pass_rate = (stats["passed"] / total * 100) if total > 0 else 0
            md += f"- **{agent}**: {stats['passed']}/{total} ({pass_rate:.1f}%)\n"
        
        if rca:
            md += f"\n## Root Cause Analysis\n"
            md += f"- **Total Failures**: {rca['total_failures']}\n\n"
            md += f"### Top Root Causes\n"
            for cause in rca.get("top_root_causes", []):
                md += f"- **{cause['category']}**: {cause['count']} ({cause['percentage']:.1f}%)\n"
            
            md += f"\n### Recommendations\n"
            for rec in rca.get("recommendations", []):
                md += f"- {rec}\n"
        
        return {
            "type": "markdown",
            "content": md
        }
    
    def _generate_html_report(
        self,
        aggregated: Dict[str, Any],
        metrics: Dict[str, Any],
        rca: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate HTML report"""
        
        status_color = "#4CAF50" if aggregated["failed"] == 0 else "#f44336"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: {status_color}; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Report</h1>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{aggregated['total']}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric">
                <div class="metric-value">{aggregated['passed']}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{aggregated['failed']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{metrics['pass_rate']:.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
        </div>
        
        <h2>Results by Agent</h2>
        <table>
            <tr>
                <th>Agent</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Pass Rate</th>
            </tr>
"""
        
        for agent, stats in aggregated["by_agent"].items():
            total = stats["passed"] + stats["failed"]
            pass_rate = (stats["passed"] / total * 100) if total > 0 else 0
            html += f"""
            <tr>
                <td>{agent}</td>
                <td>{stats['passed']}</td>
                <td>{stats['failed']}</td>
                <td>{pass_rate:.1f}%</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        
        return {
            "type": "html",
            "content": html
        }
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)"""
        pass_rate = metrics.get("pass_rate", 0)
        healing_rate = metrics.get("healing_rate", 0)
        
        # Weighted score: 70% pass rate, 30% healing rate
        health_score = (pass_rate * 0.7) + (healing_rate * 0.3)
        
        return round(health_score, 1)
    
    async def trend_analysis(
        self,
        historical_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trends across multiple reports"""
        logger.info(f"📊 Report Agent: Analyzing trends from {len(historical_reports)} reports")
        
        if len(historical_reports) < 2:
            return {"error": "Need at least 2 reports for trend analysis"}
        
        pass_rates = [r.get("metrics", {}).get("pass_rate", 0) for r in historical_reports]
        execution_times = [r.get("aggregated", {}).get("execution_time", 0) for r in historical_reports]
        
        return {
            "reports_analyzed": len(historical_reports),
            "pass_rate_trend": {
                "average": sum(pass_rates) / len(pass_rates),
                "min": min(pass_rates),
                "max": max(pass_rates),
                "latest": pass_rates[-1],
                "direction": "improving" if pass_rates[-1] > pass_rates[0] else "declining"
            },
            "execution_time_trend": {
                "average": sum(execution_times) / len(execution_times),
                "min": min(execution_times),
                "max": max(execution_times),
                "latest": execution_times[-1]
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """Return agent status"""
        return {
            "agent_type": self.agent_type,
            "name": "Report Agent",
            "role": "Analyst",
            "capabilities": self.capabilities,
            "is_available": True,
            "reports_generated": len(self.report_history)
        }

"""
Deterministic Fallback Engine
Generates structured natural language reports directly from deterministic
analytics, ML models, and agent findings when the LLM is unavailable, times out,
or violates guardrails.
"""

from typing import Dict, Any, List

class DeterministicFallbackEngine:
    @staticmethod
    def generate_fallback_response(
        query: str,
        state: Dict[str, Any],
        reason: str = "LLM unavailable or timed out"
    ) -> Dict[str, Any]:
        """Synthesizes structured response deterministically without an LLM."""
        agent_outputs = state.get("agent_outputs", {})
        ins_out = agent_outputs.get("insight_agent", {})
        sup_out = agent_outputs.get("supplier_risk_agent", {})
        del_out = agent_outputs.get("delivery_risk_agent", {})
        inv_out = agent_outputs.get("inventory_risk_agent", {})
        dmd_out = agent_outputs.get("demand_agent", {})
        rec_out = agent_outputs.get("recommendation_agent", {})

        overall_risk = ins_out.get("overall_supply_chain_risk", "MEDIUM")

        # Synthesize sections deterministically
        lines = []
        lines.append(f"**Deterministic Risk Assessment:** The overall supply chain risk level is **{overall_risk}**.")

        # Supplier segment
        if sup_out and sup_out.get("supplier_profiles"):
            top_sup = sup_out["supplier_profiles"][0]
            lines.append(
                f"**Supplier Performance:** Highest risk supplier is **{top_sup['supplier_id']}** ({top_sup['supplier_name']}), "
                f"exhibiting an overall risk score of {top_sup['supplier_risk_score']} ({top_sup['supplier_risk_level']}) "
                f"with a late delivery rate of {top_sup['late_delivery_rate']:.1%} and {top_sup['avg_delay_days']} days average delay."
            )

        # Delivery segment
        if del_out:
            lines.append(
                f"**Logistics & Delivery:** Overall cohort delay rate is {del_out.get('late_order_rate', 0.0):.1%} "
                f"across {del_out.get('total_orders_analyzed', 0):,} analyzed shipments, with ML forward late risk probability estimated at {del_out.get('ml_model_predicted_late_prob', 0.0):.1%}."
            )

        # Inventory segment
        if inv_out and inv_out.get("product_inventory_details"):
            crits = [p for p in inv_out["product_inventory_details"] if p["risk_level"] in ["CRITICAL", "HIGH"]]
            if crits:
                cp = crits[0]
                lines.append(
                    f"**Inventory Exposure:** Critical stockout threat detected for **{cp['product_id']}** ({cp['product_name']}) "
                    f"with only {cp['days_of_supply']} Days of Supply remaining. Projected stock-out date: {cp['projected_stockout_date']}. "
                    f"Deterministic recommended reorder quantity: {cp['recommended_reorder_quantity']:,} units."
                )

        # Demand segment
        if dmd_out and "total_projected_demand" in dmd_out:
            lines.append(
                f"**Demand Forecast:** 30-day projected demand for {dmd_out['target_product_id']} is {dmd_out['total_projected_demand']:,} units "
                f"(Model evaluation MAPE: {dmd_out['evaluation_metrics'].get('mape', 0.0)}%)."
            )

        # Key recommendations
        recs = rec_out.get("recommendations", [])
        if recs:
            top_rec = recs[0]
            lines.append(f"**Recommended Action [{top_rec['priority']}]:** {top_rec['action']} (Rationale: {top_rec['rationale']})")

        natural_language_answer = "\n\n".join(lines)

        return {
            "natural_language_answer": natural_language_answer,
            "risk_assessment_summary": f"System in {overall_risk} risk state based on deterministic rule analysis.",
            "key_findings": [
                f"Overall System Risk: {overall_risk}",
                f"Suppliers analyzed: {sup_out.get('suppliers_analyzed', 0) if sup_out else 0}",
                f"Critical Stockout SKUs: {inv_out.get('critical_stockouts_count', 0) if inv_out else 0}",
                f"Actionable Recommendations: {len(recs)}"
            ],
            "claims_made": [
                f"Overall supply chain risk is {overall_risk}",
                f"Deterministic fallback executed due to: {reason}"
            ],
            "fallback_used": True,
            "fallback_reason": reason,
            "source": "Deterministic Rule & Analytics Engine"
        }

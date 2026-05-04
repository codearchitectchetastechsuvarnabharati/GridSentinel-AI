def explain_with_local_llm(risk_score, peer_reason, zone_risk):
    if risk_score >= 0.8:
        return (
            f"High-risk behavior detected. "
            f"The meter deviates from peers ({peer_reason}) "
            f"during a {zone_risk} load stress period."
        )
    elif risk_score >= 0.6:
        return (
            "Moderate deviation observed; may reflect operational or seasonal variation."
        )
    else:
        return "Consumption pattern appears normal within current context."
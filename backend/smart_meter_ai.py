import pandas as pd
from sklearn.ensemble import IsolationForest

from ai.demand_forecasting import forecast_zone_demand
from ai.peer_analysis import peer_group_analysis
from local_llm_stub import explain_with_local_llm


def run_smart_meter_ai_pipeline(csv_path):
    """
    GridSentinel AI – Core Analytics Pipeline

    PART A:
      - Localized demand prediction (zone level)
    PART B:
      - Anomaly detection (meter level)
      - Peer comparison
      - Composite risk scoring
    """

    # -------------------------------------------------
    # Load and sanitize data
    # -------------------------------------------------
    df = pd.read_csv(csv_path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.sort_values(by=df.columns.tolist())

    # -------------------------------------------------
    # PART A: Demand Forecasting (Zone Level)
    # -------------------------------------------------
    zone_df = forecast_zone_demand(df)

    # ✅ Ensure stress_ratio exists
    if "stress_ratio" not in zone_df.columns:
        zone_df["stress_ratio"] = 0.0

    # ✅ Explicit zone risk classification
    zone_df["risk_level"] = zone_df["stress_ratio"].apply(
        lambda x: "HIGH" if x >= 1.1 else
                  "MEDIUM" if x >= 0.95 else
                  "LOW"
    )

    # -------------------------------------------------
    # PART B: Anomaly Detection (Meter Level)
    # -------------------------------------------------
    iso = IsolationForest(
        contamination=0.15,
        random_state=42
    )

    df["anomaly_flag"] = iso.fit_predict(df[["consumption"]])
    df["anomaly_score"] = df["anomaly_flag"].map({-1: 1.0, 1: 0.0})

    # -------------------------------------------------
    # Peer Group Analysis (ALWAYS returns columns)
    # -------------------------------------------------
    peer_df = peer_group_analysis(df)

    df = df.merge(
        peer_df,
        on=["meter_id", "zone_id"],
        how="left"
    )

    # ✅ DEFENSIVE GUARDS (critical)
    if "peer_deviation" not in df.columns:
        df["peer_deviation"] = 0.0

    if "peer_reason" not in df.columns:
        df["peer_reason"] = "Peer comparison unavailable"

    # -------------------------------------------------
    # Merge zone-level stress info
    # -------------------------------------------------
    df = df.merge(
        zone_df[["zone_id", "stress_ratio", "risk_level"]],
        on="zone_id",
        how="left"
    )

    df["stress_ratio"] = df["stress_ratio"].fillna(0.0)
    df["risk_level"] = df["risk_level"].fillna("LOW")

    # -------------------------------------------------
    # Composite Risk Score (Explainable)
    # -------------------------------------------------
    df["final_risk_score"] = (
        0.4 * df["anomaly_score"] +
        0.3 * df["peer_deviation"] +
        0.3 * df["stress_ratio"]
    ).round(2)

    # -------------------------------------------------
    # Explanation Layer (Decision Support Only)
    # -------------------------------------------------
    df["reason"] = df.apply(
        lambda r: explain_with_local_llm(
            r["final_risk_score"],
            r["peer_reason"],
            r["risk_level"]
        ),
        axis=1
    )

    # -------------------------------------------------
    # Inspection Candidate List
    # -------------------------------------------------
    inspections = df[df["final_risk_score"] >= 0.7][[
        "meter_id",
        "zone_id",
        "final_risk_score",
        "reason"
    ]].rename(columns={
        "final_risk_score": "risk_score"
    })

    return zone_df, inspections
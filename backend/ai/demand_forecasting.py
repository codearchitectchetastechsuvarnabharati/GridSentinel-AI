import pandas as pd

def forecast_zone_demand(df, window=4):
    results = []

    for zone, zdf in df.groupby("zone_id"):
        zdf = zdf.sort_values("timestamp")
        recent = zdf["consumption"].tail(window)

        rolling_avg = recent.mean()
        ewma = recent.ewm(span=window).mean().iloc[-1]
        forecast = max(rolling_avg, ewma)
        peak = zdf["consumption"].max()

        stress_ratio = forecast / peak if peak else 0

        risk = (
            "HIGH" if stress_ratio >= 1.1 else
            "MEDIUM" if stress_ratio >= 0.95 else
            "LOW"
        )

        results.append({
            "zone_id": zone,
            "forecast_load": round(forecast, 2),
            "historical_peak": round(peak, 2),
            "stress_ratio": round(stress_ratio, 2),
            "risk_level": risk,
            "forecast_reason": "Rolling mean + EWMA short-term forecast"
        })

    return pd.DataFrame(results)
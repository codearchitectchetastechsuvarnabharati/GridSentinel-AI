import pandas as pd

def peer_group_analysis(df):
    rows = []

    for zone, zdf in df.groupby("zone_id"):
        avg = zdf["consumption"].mean()

        for _, r in zdf.iterrows():
            deviation = (avg - r["consumption"]) / avg if avg else 0

            reason = (
                "Significantly below peer average" if deviation >= 0.5 else
                "Moderately below peer average" if deviation >= 0.3 else
                "Within normal peer range"
            )

            rows.append({
                "meter_id": r["meter_id"],
                "zone_id": zone,
                "peer_deviation": abs(round(deviation, 2)),
                "peer_reason": reason
            })

    return pd.DataFrame(rows)
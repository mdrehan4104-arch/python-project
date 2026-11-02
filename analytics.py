import pandas as pd


def build_summary(df):
    if df.empty:
        return {"records": 0, "prepared": 0.0, "served": 0.0, "leftover": 0.0, "waste_rate": 0.0}
    prepared = float(df["prepared_kg"].sum())
    served = float(df["served_kg"].sum())
    leftover = float(df["leftover_kg"].sum())
    waste_rate = (leftover / prepared * 100) if prepared else 0.0
    return {
        "records": int(len(df)),
        "prepared": prepared,
        "served": served,
        "leftover": leftover,
        "waste_rate": waste_rate,
    }


def category_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["food_item", "leftover_kg"])
    return (
        df.groupby("food_item", as_index=False)["leftover_kg"]
        .sum()
        .sort_values("leftover_kg", ascending=False)
    )


def daily_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["date", "prepared_kg", "leftover_kg"])
    result = df.groupby("date", as_index=False)[["prepared_kg", "leftover_kg"]].sum()
    result["date"] = pd.to_datetime(result["date"])
    return result.sort_values("date")


def meal_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["meal", "prepared_kg", "leftover_kg"])
    return df.groupby("meal", as_index=False)[["prepared_kg", "leftover_kg"]].sum()


def generate_insights(df):
    if df.empty:
        return ["Add food logs to see insights."]
    insights = []
    summary = build_summary(df)
    insights.append(
        f"Across {summary['records']} records, {summary['leftover']:.2f} kg was left over "
        f"out of {summary['prepared']:.2f} kg prepared ({summary['waste_rate']:.1f}% by weight)."
    )

    food = category_summary(df)
    if not food.empty:
        top = food.iloc[0]
        insights.append(
            f"'{top['food_item']}' has the highest recorded leftover quantity "
            f"({top['leftover_kg']:.2f} kg). Review portion sizes or demand for this item."
        )

    meals = meal_summary(df)
    if not meals.empty:
        meals["waste_rate"] = meals.apply(
            lambda row: (row["leftover_kg"] / row["prepared_kg"] * 100)
            if row["prepared_kg"] else 0,
            axis=1,
        )
        top_meal = meals.sort_values("waste_rate", ascending=False).iloc[0]
        insights.append(
            f"{top_meal['meal']} has the highest meal-level waste rate in this dataset "
            f"({top_meal['waste_rate']:.1f}%). Compare more days before changing preparation."
        )

    if summary["waste_rate"] >= 15:
        insights.append("Waste is at least 15% overall. Review attendance, menu preferences, and batch sizes.")
    else:
        insights.append("Keep monitoring daily records to check whether the current waste rate is improving.")

    if len(df) < 7:
        insights.append("Data note: fewer than 7 records are available, so these patterns are preliminary.")
    return insights

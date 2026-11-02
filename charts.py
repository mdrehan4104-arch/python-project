import plotly.express as px
import plotly.graph_objects as go


def category_bar_chart(summary_df):
    fig = px.bar(
        summary_df.sort_values("leftover_kg", ascending=True),
        x="leftover_kg",
        y="food_item",
        orientation="h",
        title="Leftovers by food item",
        labels={"leftover_kg": "Leftover (kg)", "food_item": "Food item"},
        color="leftover_kg",
        color_continuous_scale="Greens",
    )
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def meal_waste_chart(df):
    grouped = df.groupby("meal", as_index=False)[["prepared_kg", "leftover_kg"]].sum()
    grouped["waste_rate"] = grouped.apply(
        lambda row: row["leftover_kg"] / row["prepared_kg"] * 100 if row["prepared_kg"] else 0,
        axis=1,
    )
    fig = px.bar(
        grouped,
        x="meal",
        y="waste_rate",
        title="Waste rate by meal",
        labels={"meal": "Meal", "waste_rate": "Waste rate (%)"},
        color="waste_rate",
        color_continuous_scale="Oranges",
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_ticksuffix="%", margin=dict(l=10, r=10, t=50, b=10))
    return fig


def daily_trend_chart(daily_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_df["date"], y=daily_df["prepared_kg"],
        mode="lines+markers", name="Prepared (kg)"
    ))
    fig.add_trace(go.Scatter(
        x=daily_df["date"], y=daily_df["leftover_kg"],
        mode="lines+markers", name="Leftover (kg)"
    ))
    fig.update_layout(
        title="Daily food preparation vs leftovers",
        xaxis_title="Date",
        yaxis_title="Quantity (kg)",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

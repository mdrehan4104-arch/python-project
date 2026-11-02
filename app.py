import pandas as pd
import streamlit as st

from analytics import build_summary, category_summary, daily_summary, generate_insights
from charts import category_bar_chart, daily_trend_chart, meal_waste_chart
from database import (
    add_record, delete_record, fetch_records, init_db, update_record
)

st.set_page_config(
    page_title="WasteWise | Food Waste Analytics",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

st.markdown("""
<style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        background: #f5f8f5;
        border: 1px solid #e0e9e0;
        padding: 15px;
        border-radius: 12px;
    }
    .subtitle {color: #617064; margin-top: -10px;}
</style>
""", unsafe_allow_html=True)

st.title("🌱 WasteWise")
st.markdown('<p class="subtitle">Smart food waste tracking and analytics for campus messes and cafeterias.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["Dashboard", "Add Food Log", "Manage Records", "Insights & Export"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("WasteWise • Python Data Analytics Project")
    st.caption("Use consistent units (kg) for all quantities.")

records = fetch_records()
df = pd.DataFrame(records)

if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date

if page == "Dashboard":
    st.subheader("Overview")
    if df.empty:
        st.info("No records yet. Open **Add Food Log** to enter your first meal record, or load the sample CSV from **Insights & Export**.")
        st.metric("Food prepared", "0.00 kg")
        st.metric("Food wasted", "0.00 kg")
        st.metric("Waste rate", "0.0%")
    else:
        summary = build_summary(df)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records", f"{summary['records']:,}")
        c2.metric("Food prepared", f"{summary['prepared']:.2f} kg")
        c3.metric("Food wasted", f"{summary['leftover']:.2f} kg")
        c4.metric("Waste rate", f"{summary['waste_rate']:.1f}%")

        st.markdown("### Waste patterns")
        left, right = st.columns(2)
        with left:
            st.plotly_chart(category_bar_chart(category_summary(df)), use_container_width=True)
        with right:
            st.plotly_chart(meal_waste_chart(df), use_container_width=True)
        st.plotly_chart(daily_trend_chart(daily_summary(df)), use_container_width=True)

        st.markdown("### Recent records")
        st.dataframe(df.sort_values(["date", "id"], ascending=False).head(10), use_container_width=True, hide_index=True)

elif page == "Add Food Log":
    st.subheader("Add a food-waste record")
    st.caption("Record one food item for one meal. Use kilograms for all quantities.")
    with st.form("add_record_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Date")
            meal = st.selectbox("Meal", ["Breakfast", "Lunch", "Snacks", "Dinner"])
            food_item = st.text_input("Food item", placeholder="e.g., Rice, Dal, Chapati")
        with c2:
            prepared = st.number_input("Food prepared (kg)", min_value=0.0, max_value=10000.0, value=10.0, step=0.5)
            served = st.number_input("Food served (kg)", min_value=0.0, max_value=10000.0, value=8.0, step=0.5)
            leftover = st.number_input("Leftover / wasted (kg)", min_value=0.0, max_value=10000.0, value=2.0, step=0.5)
        notes = st.text_input("Notes (optional)", placeholder="e.g., lower attendance due to holiday")
        submitted = st.form_submit_button("Save food log", type="primary", use_container_width=True)

    if submitted:
        if not food_item.strip():
            st.error("Please enter a food item.")
        elif prepared <= 0:
            st.error("Food prepared must be greater than zero.")
        elif served + leftover > prepared + 1e-9:
            st.error("Served quantity plus leftover quantity cannot exceed prepared quantity.")
        else:
            add_record(str(date), meal, food_item.strip(), prepared, served, leftover, notes.strip())
            st.success("Food log saved successfully.")
            st.info("Open Dashboard to view updated analytics.")

elif page == "Manage Records":
    st.subheader("Manage food logs")
    if df.empty:
        st.info("No records available to manage yet.")
    else:
        display = df.copy()
        display["date"] = display["date"].astype(str)
        st.dataframe(display, use_container_width=True, hide_index=True)
        ids = display["id"].tolist()
        selected_id = st.selectbox("Select record ID", ids)
        selected = next(row for row in records if row["id"] == selected_id)
        with st.expander("Edit selected record"):
            with st.form("edit_record_form"):
                c1, c2 = st.columns(2)
                with c1:
                    edit_date = st.date_input("Date", value=pd.to_datetime(selected["date"]).date(), key="edit_date")
                    edit_meal = st.selectbox("Meal", ["Breakfast", "Lunch", "Snacks", "Dinner"], index=["Breakfast", "Lunch", "Snacks", "Dinner"].index(selected["meal"]), key="edit_meal")
                    edit_food = st.text_input("Food item", value=selected["food_item"], key="edit_food")
                with c2:
                    edit_prepared = st.number_input("Prepared (kg)", min_value=0.0, value=float(selected["prepared_kg"]), step=0.5, key="edit_prepared")
                    edit_served = st.number_input("Served (kg)", min_value=0.0, value=float(selected["served_kg"]), step=0.5, key="edit_served")
                    edit_leftover = st.number_input("Leftover (kg)", min_value=0.0, value=float(selected["leftover_kg"]), step=0.5, key="edit_leftover")
                edit_notes = st.text_input("Notes", value=selected.get("notes", ""), key="edit_notes")
                edit_submit = st.form_submit_button("Update record")
            if edit_submit:
                if not edit_food.strip():
                    st.error("Food item cannot be empty.")
                elif edit_prepared <= 0:
                    st.error("Prepared quantity must be greater than zero.")
                elif edit_served + edit_leftover > edit_prepared + 1e-9:
                    st.error("Served plus leftover cannot exceed prepared quantity.")
                else:
                    update_record(selected_id, str(edit_date), edit_meal, edit_food.strip(), edit_prepared, edit_served, edit_leftover, edit_notes.strip())
                    st.success("Record updated. Refreshing data...")
                    st.rerun()
        with st.expander("Delete selected record"):
            st.warning("Deleting a record cannot be undone.")
            confirm = st.checkbox(f"Confirm deletion of record #{selected_id}")
            if st.button("Delete record", disabled=not confirm):
                delete_record(selected_id)
                st.success("Record deleted.")
                st.rerun()

elif page == "Insights & Export":
    st.subheader("Insights and data export")
    if df.empty:
        st.info("There are no records yet. Add logs or import the included sample dataset.")
    else:
        for insight in generate_insights(df):
            st.markdown(f"- {insight}")
        st.markdown("### Export current records")
        export_df = df.copy()
        export_df["date"] = export_df["date"].astype(str)
        st.download_button(
            "Download records as CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="wastewise_records.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.divider()
    st.markdown("### Import records from CSV")
    st.caption("Required columns: date, meal, food_item, prepared_kg, served_kg, leftover_kg. Optional column: notes.")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded is not None and st.button("Import CSV records"):
        try:
            import_df = pd.read_csv(uploaded)
            required = {"date", "meal", "food_item", "prepared_kg", "served_kg", "leftover_kg"}
            missing = required - set(import_df.columns)
            if missing:
                st.error("Missing required columns: " + ", ".join(sorted(missing)))
            else:
                imported = 0
                errors = []
                for index, row in import_df.iterrows():
                    try:
                        date_text = pd.to_datetime(row["date"], errors="raise").date().isoformat()
                        meal_text = str(row["meal"]).strip().title()
                        food_text = str(row["food_item"]).strip()
                        prepared_value = float(row["prepared_kg"])
                        served_value = float(row["served_kg"])
                        leftover_value = float(row["leftover_kg"])
                        notes_value = "" if pd.isna(row.get("notes", "")) else str(row.get("notes", ""))
                        if meal_text not in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
                            raise ValueError("meal must be Breakfast, Lunch, Snacks, or Dinner")
                        if not food_text or prepared_value <= 0 or served_value < 0 or leftover_value < 0:
                            raise ValueError("invalid food item or quantity")
                        if served_value + leftover_value > prepared_value + 1e-9:
                            raise ValueError("served + leftover exceeds prepared")
                        add_record(date_text, meal_text, food_text, prepared_value, served_value, leftover_value, notes_value)
                        imported += 1
                    except Exception as exc:
                        errors.append(f"Row {index + 2}: {exc}")
                st.success(f"Imported {imported} valid record(s).")
                if errors:
                    st.warning("Some rows were skipped:\n\n" + "\n".join(errors[:10]))
                st.rerun()
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

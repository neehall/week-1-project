"""
Generates synthetic Cost, Capex, and Opex datasets aligned with the
existing sales_data.csv (same date range and regions), so the Cost,
Capex, and Opex dashboards have realistic data to render.

Re-run any time to regenerate (deterministic via fixed random seed):
    python3 data/generate_synthetic_data.py
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(seed=42)

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"


def _monthly_dates():
    return pd.date_range(START_DATE, END_DATE, freq="MS")  # month start


def generate_cost_data(path="data/cost_data.csv"):
    """Cost of doing business: COGS, Logistics, Marketing, Admin — by region/month."""
    categories = ["COGS", "Logistics", "Marketing", "Admin"]
    base_by_category = {"COGS": 45000, "Logistics": 12000, "Marketing": 9000, "Admin": 6000}

    rows = []
    for month in _monthly_dates():
        for region in REGIONS:
            region_factor = RNG.uniform(0.7, 1.3)
            for category in categories:
                base = base_by_category[category] * region_factor
                seasonal = 1 + 0.15 * np.sin(2 * np.pi * month.month / 12)
                noise = RNG.uniform(0.85, 1.15)
                amount = round(base * seasonal * noise, 2)
                rows.append(
                    {
                        "date": month.date().isoformat(),
                        "region": region,
                        "cost_category": category,
                        "amount": amount,
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


def generate_capex_data(path="data/capex_data.csv"):
    """Capital expenditure: discrete project-based spend by asset category."""
    asset_categories = ["IT Equipment", "Machinery", "Buildings", "Vehicles", "Software Licenses"]
    project_prefixes = {
        "IT Equipment": "Server Refresh",
        "Machinery": "Plant Upgrade",
        "Buildings": "Facility Expansion",
        "Vehicles": "Fleet Renewal",
        "Software Licenses": "Platform Modernization",
    }

    n_projects = 90
    rows = []
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    for i in range(n_projects):
        asset_category = RNG.choice(asset_categories)
        region = RNG.choice(REGIONS)
        date = RNG.choice(dates)
        amount = round(float(RNG.uniform(5000, 250000)), 2)
        rows.append(
            {
                "date": pd.Timestamp(date).date().isoformat(),
                "region": region,
                "asset_category": asset_category,
                "project_name": f"{project_prefixes[asset_category]} #{i + 1}",
                "amount": amount,
            }
        )
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df.to_csv(path, index=False)
    return df


def generate_opex_data(path="data/opex_data.csv"):
    """Operating expense: recurring spend by department/expense type."""
    departments = ["Sales", "Marketing", "R&D", "Admin", "Operations"]
    expense_types = ["Salaries", "Rent", "Utilities", "Travel", "Software", "Professional Services"]
    base_by_type = {
        "Salaries": 60000,
        "Rent": 15000,
        "Utilities": 4000,
        "Travel": 3000,
        "Software": 5000,
        "Professional Services": 6000,
    }

    rows = []
    for month in _monthly_dates():
        for region in REGIONS:
            region_factor = RNG.uniform(0.7, 1.3)
            for department in departments:
                dept_factor = RNG.uniform(0.8, 1.2)
                for expense_type in expense_types:
                    # not every department incurs every expense type every month
                    if RNG.random() < 0.25:
                        continue
                    base = base_by_type[expense_type] * region_factor * dept_factor
                    noise = RNG.uniform(0.85, 1.15)
                    amount = round(base * noise / len(departments), 2)
                    rows.append(
                        {
                            "date": month.date().isoformat(),
                            "region": region,
                            "department": department,
                            "expense_type": expense_type,
                            "amount": amount,
                        }
                    )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    cost_df = generate_cost_data()
    capex_df = generate_capex_data()
    opex_df = generate_opex_data()
    print(f"cost_data.csv:  {len(cost_df)} rows")
    print(f"capex_data.csv: {len(capex_df)} rows")
    print(f"opex_data.csv:  {len(opex_df)} rows")

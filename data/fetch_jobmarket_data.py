"""
Downloads the real "Ask a Manager" salary survey (2019) — a large,
public, crowd-sourced survey of real self-reported job title,
industry, experience, location, and annual salary — mirrored as a
plain CSV at github.com/kmamykin/askamanager_salary_survey.

Writes data/jobmarket_salaries.csv with columns:
    job_title, industry, experience, city, state, salary

Filtered to US respondents paid in USD, salaries cleaned to numeric
and bounded to a plausible range ($15k-$500k, dropping data-entry
errors like a reported $15.6M salary), and the top 20 best-represented
cities (for chart readability, same curated-city approach as the
Climate/Real Estate dashboards).

Note: this real survey has no "skills required" field — it captures
job title, industry, experience, and salary, not skill listings. The
Job Market dashboard surfaces salary distributions by role/industry
and demand by city (both real), not a skills-trend chart, rather than
inventing a skills column that isn't in the real data. See
SESSION_LOG.md.

Re-run to refresh (network required):
    python3 data/fetch_jobmarket_data.py
"""
import pandas as pd
import requests

URL = "https://raw.githubusercontent.com/kmamykin/askamanager_salary_survey/master/data/v1/Ask-A-Manager-Salary-Survey-2019.csv"
SALARY_MIN, SALARY_MAX = 15_000, 500_000
TOP_N_CITIES = 20


def main(path: str = "data/jobmarket_salaries.csv"):
    resp = requests.get(URL, timeout=60)
    resp.raise_for_status()
    resp.encoding = "latin-1"  # source file isn't strict UTF-8
    df = pd.read_csv(pd.io.common.StringIO(resp.text))

    df["salary"] = pd.to_numeric(df["AnnualSalary"].astype(str).str.replace(",", ""), errors="coerce")
    df = df[(df["Country"] == "USA") & (df["Currency"] == "USD")]
    df = df[df["salary"].between(SALARY_MIN, SALARY_MAX)]
    df = df.dropna(subset=["City", "Industry (Clustered)", "Experience", "JobTitle"])

    top_cities = df["City"].value_counts().head(TOP_N_CITIES).index
    df = df[df["City"].isin(top_cities)]

    out = df.rename(
        columns={
            "JobTitle": "job_title",
            "Industry (Clustered)": "industry",
            "Experience": "experience",
            "City": "city",
            "State": "state",
        }
    )[["job_title", "industry", "experience", "city", "state", "salary"]]
    out.to_csv(path, index=False)
    print(f"{path}: {len(out)} rows, {out['city'].nunique()} cities, {out['industry'].nunique()} industries")


if __name__ == "__main__":
    main()

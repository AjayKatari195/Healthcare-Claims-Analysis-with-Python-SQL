"""Simple healthcare claims analysis using Python, pandas and SQL (SQLite).
Uses synthetic data - no real patient information."""
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create_data(n=1000, seed=42):
    """Create a small, messy claims dataset."""
    rng = np.random.default_rng(seed)
    payers = ["Aetna", "Cigna", "BlueCross", "Medicare"]
    reasons = ["Prior Authorization Missing", "Incorrect Coding", "Out of Network", "Missing Documentation"]
    status = rng.choice(["Paid", "Denied"], size=n, p=[0.8, 0.2])
    df = pd.DataFrame({
        "claim_id": range(1, n + 1),
        "payer": rng.choice(payers, size=n),
        "billed_amount": rng.integers(200, 5000, size=n).astype(float),
        "status": status,
        "denial_reason": np.where(status == "Denied", rng.choice(reasons, size=n, p=[.4, .3, .2, .1]), None),
    })
    df["payer"] = df["payer"].map(lambda p: rng.choice([p, p.upper(), f" {p} "], p=[.8, .1, .1]))  # messy names
    df.loc[rng.choice(n, 20, replace=False), "billed_amount"] = np.nan                              # missing values
    return pd.concat([df, df.sample(30, random_state=seed)], ignore_index=True)                      # duplicates


def clean_data(df):
    """Remove duplicates, fix payer names, drop missing amounts."""
    df = df.drop_duplicates(subset="claim_id")
    df["payer"] = df["payer"].str.strip().str.title().replace({"Bluecross": "BlueCross"})
    return df.dropna(subset=["billed_amount"])


def denial_rate_by_payer(df):
    """Denial rate (%) for each payer."""
    return ((df["status"] == "Denied").groupby(df["payer"]).mean() * 100).round(1).sort_values(ascending=False)


def top_denial_reasons(df):
    """Run a SQL query on the cleaned data."""
    conn = sqlite3.connect(":memory:")
    df.to_sql("claims", conn, index=False)
    query = """
        SELECT denial_reason, COUNT(*) AS denials, ROUND(SUM(billed_amount), 0) AS denied_value
        FROM claims WHERE status = 'Denied'
        GROUP BY denial_reason ORDER BY denials DESC
    """
    return pd.read_sql_query(query, conn)


if __name__ == "__main__":
    raw = create_data()
    clean = clean_data(raw)
    print(f"Rows: {len(raw)} raw -> {len(clean)} clean")
    print("\nDenial rate by payer (%):\n", denial_rate_by_payer(clean))
    reasons = top_denial_reasons(clean)
    print("\nTop denial reasons:\n", reasons)

    reasons.plot.bar(x="denial_reason", y="denials", legend=False, color="#1F3864", title="Denials by Reason")
    plt.tight_layout()
    plt.savefig("denial_reasons.png")
    print("\nSaved chart: denial_reasons.png")

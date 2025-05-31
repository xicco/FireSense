import pandas as pd

def add_season_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add calendar‐season labels to a DataFrame based on its datetime index.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must contain a column named "time" of dtype datetime64[ns].

    Returns
    -------
    pd.DataFrame
        A shallow copy of the input with two new columns:
        - "month": integer month (1–12) extracted from "time"
        - "season": calendar season string, one of ["winter","spring","summer","autumn"]
    """
    # 1. Work on a copy to avoid mutating the original
    df = df.copy()

    # 2. Extract month and map to season
    df["month"] = df["time"].dt.month
    df["season"] = df["month"].map({
        12:"winter", 1:"winter", 2:"winter",
        3:"spring", 4:"spring", 5:"spring",
        6:"summer",7:"summer",8:"summer",
        9:"autumn",10:"autumn",11:"autumn"
    })

    return df


def compute_threshold(df: pd.DataFrame, pct: float = 10.0) -> pd.DataFrame:
    """
    Compute seasonal moisture thresholds for each grid cell.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    pct : float, default 10.0
        The percentile (0–100) to use as the “dry baseline.”  
        For example, pct=10 means the 10th percentile moisture.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with columns:
          - "lat"       (float)
          - "lon"       (float)
          - "season"    (str: "winter", "spring", "summer", "autumn")
          - "threshold" (float moisture value at the given percentile)
    """
    # 1. Tag each row with its season
    df2 = add_season_column(df)

    # 2. Compute the pct-th percentile threshold per (lat, lon, season)
    thr = (
        df2
        .groupby(["lat", "lon", "season"])["moisture"]      # split into groups
        .quantile(pct/100)                                  # compute percentile
        .reset_index()                                      # turn index levels into columns
        .rename(columns={"moisture":"threshold"})           # rename percentile col
    )

    return thr


def classify_risk(df: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    """
    Join moisture data with seasonal thresholds and compute fire‐risk flags and scores.

    Inputs:
    - df: DataFrame with columns time, lat, lon, moisture (and no NaNs)
    - thresholds: DataFrame with columns lat, lon, season, threshold

    Output:
    - df2: copy of df with extra columns:
        • season (from time)
        • threshold (matched by lat, lon, season)
        • risk_flag (True if moisture < threshold)
        • risk_score (how far below threshold, scaled 0–∞, clipped to ≥0)
    """
    # 1. Tag each row with its calendar season
    df2 = add_season_column(df)

    # 2. Bring in the matching threshold value
    df2 = df2.merge(
        thresholds,
        on=["lat", "lon", "season"],
        how="left"
    )

    # 3. Create a boolean flag for “at‐risk” moisture
    df2["risk_flag"] = df2["moisture"] < df2["threshold"]

    # 4. Compute a continuous “risk” score
    df2["risk_score"] = (
        (df2["threshold"] - df2["moisture"])    # positive if moisture < threshold
        / df2["threshold"]                      # scale relative to the baseline
    ).clip(lower=0)

    # 5. Return the augmented DataFrame
    return df2


if __name__ == "__main__":
    from dataframe import load_multiple_files

    import os
    data_folder = "data/daily/"
    all_files = []
    for file in os.listdir(data_folder):
        if file.endswith(".nc"):
            full_path = os.path.join(data_folder, file)
            all_files.append(full_path)
    df_multiple = load_multiple_files(all_files, ["sm", "sm_uncertainty"])

    df2 = add_season_column(df_multiple)
    thresholds = compute_threshold(df2, 10.0)
    df_risk = classify_risk(df2, thresholds)

    print (df_risk.head(15))
    print(df_risk.sort_values("risk_score", ascending=False).head(10))
    print(df_risk["risk_flag"].value_counts())

    num_zero = (df_risk["risk_score"] == 0).sum()
    print(f"Number of rows with risk_score == 0: {num_zero}")


# think about the various locations that are visible in each data.
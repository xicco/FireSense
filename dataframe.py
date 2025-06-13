import xarray as xr
import pandas as pd
from typing import Union

def netcdf_to_pandas(source: Union[str, xr.Dataset], variable: Union[str, list[str]] = "sm") -> pd.DataFrame:
    """
    Loads soil moisture data from a NetCDF file (or xarray.Dataset) and converts it into a pandas DataFrame.

    Preconditions:
        - source: str or xr.Dataset
                    Path to the .nc file or an already opened xarray.Dataset.
        - variable: str or list
                    Name of the data variable to extract, default is 'sm'.
    
    """
    # 1. Normalize variable input
    if isinstance(variable, str):
        var_list = [variable]
    else:
        var_list = variable

    # 2–4. Open (and auto-close) dataset, select vars, flatten
    if isinstance(source, str):
        with xr.open_dataset(source) as ds:
            da = ds[var_list]
            df = da.to_dataframe().reset_index()
    
    else:
        da = source[var_list]
        df = da.to_dataframe().reset_index()

    # 5. Build rename map
    rename_map = {}
    for v in var_list:
        if v == "sm":
            rename_map[v] = "moisture"
        elif v == "sm_uncertainty":
            rename_map[v] = "uncertainty"
        else:
            rename_map[v] = v

    # 6. Rename and 7. drop NaNs
    df = df.rename(columns=rename_map)
    df = df.dropna(subset=list(rename_map.values()))


    return df


def load_multiple_files(file_list: list[str], variable: Union[str, list[str]] = "sm") -> pd.DataFrame:
    """
    Loads multiple NetCDF files, converts each to a DataFrame, and concatenates them.

    Args:
        file_list: list of file paths to NetCDF files (one file per day).
        variable: variable or list of variables to extract, default "sm".
    
    Returns:
        A single pandas DataFrame containing data from all files concatenated.
    """
    dfs = []    # list to hold individual DataFrames
    for file in file_list:
        df = netcdf_to_pandas(file, variable)   # use existing function to load each file
        dfs.append(df) # add to list

    # concatenate all DataFrames vertically, reset index to avoid duplicates
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def load_fire_data(csv_path: str) -> pd.DataFrame:
    """
    Loads NASA FIRMS fire data from a CSV file and returns a cleaned DataFrame.

    Args:
        csv_path (str): Path to the fire data CSV file.

    Returns:
        pd.DataFrame: Cleaned fire data with latitude, longitude, brightness, and time.
    """
    df = pd.read_csv(csv_path)

    # Basic filtering and renaming
    df = df.rename(columns={
        'latitude': 'lat',
        'longitude': 'lon',
        'acq_date': 'date',
        'acq_time': 'time',
        'brightness': 'brightness'
    })

    # Convert data column to datetime
    df['date'] = pd.to_datetime(df['date'])



if __name__ == "__main__":
    print("=== Testing netcdf_to_pandas with single file ===")
    path_to_file = "data/C3S-SOILMOISTURE-L3S-SSMV-COMBINED-DAILY-20230101000000-TCDR-v202312.0.0.nc"
    df = netcdf_to_pandas(path_to_file, ["sm", "sm_uncertainty"])
    print (df.head(15))
    print (df.describe())
    print(f"Single DataFrame shape: {df.shape}")

    print("\n=== Testing load_multiple_files with multiple files ===")
    import os
    data_folder = "data/daily/"
    all_files = []
    for file in os.listdir(data_folder):
        if file.endswith(".nc"):
            full_path = os.path.join(data_folder, file)
            all_files.append(full_path)
    df_multiple = load_multiple_files(all_files, ["sm", "sm_uncertainty"])
    print(df_multiple.head(15))
    print(f"Combined DataFrame shape: {df_multiple.shape}")

    print("\n=== Testing load_fire_data with single file ===")
    csv_path = ""
    df = pd.read_csv(csv_path)
    print(df['acq_date'].unique())

    fire_df = load_fire_data(fire_path)
    print(fire_df.head())
    print(f"Total records: {len(fire_df)}")
    print(f"Date range: {fire_df['date'].min()} to {fire_df['date'].max()}")
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

if __name__ == "__main__":
    path_to_file = "data/C3S-SOILMOISTURE-L3S-SSMV-COMBINED-DAILY-20230101000000-TCDR-v202312.0.0.nc"
    df = netcdf_to_pandas(path_to_file, ["sm", "sm_uncertainty"])
    print (df.head(15))
    print (df.describe())

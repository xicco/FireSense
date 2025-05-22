import xarray as xr
import pandas as pd
from typing import Union

def netcdf_to_pandas(source: Union[str, xr.Dataset], variable: str = "sm") -> pd.DataFrame:
    """
    Loads soil moisture data from a NetCDF file (or xarray.Dataset) and converts it into a pandas DataFrame.

    Preconditions:
        - source: str or xr.Dataset
                    Path to the .nc file or an already opened xarray.Dataset.
        - variable: str
                    Name of the data variable to extract, default is 'sm' or 'soil_moisture'.
    
    """
    # Case 1: source is a filepath -> use context manager
    if isinstance(source, str):
        # the dataset is opened and closed automatically when the with-block ends
        with xr.open_dataset(source) as ds:
            da = ds[variable]
            # convert, rename, and clean inside the block
            df = (
              da.to_dataframe()
                .reset_index()
                .rename(columns={variable: "moisture"})
                .dropna(subset=["moisture"])
            )
    # Case 2: source is already an xarray.Dataset or DataArray
    else:
        ds = source
        da = ds[variable]
        df = (
              da.to_dataframe()
                .reset_index()
                .rename(columns={variable: "moisture"})
                .dropna(subset=["moisture"])
            )

    return df

if __name__ == "__main__":
    path_to_file = "data/C3S-SOILMOISTURE-L3S-SSMV-COMBINED-DAILY-20230101000000-TCDR-v202312.0.0.nc"
    df = netcdf_to_pandas(path_to_file, "sm")
    print (df.head(15))
    print (df.describe())
    


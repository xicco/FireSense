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
                    Name of the data variable to extract, default is 'volumetric_surface_soil_moisture'.
    
    """
    # 1. Load or accept the dataset
    # Checks whether source is a file path, if so, opens it using xarray method, else source must be an already opened xarray.Dataset (or DataArray)
    if isinstance(source, str):
        ds = xr.open_dataset(source)
    else:
        ds = source

    # 2. Extract the DataArray that's specific to variable
    da = ds[variable]

    # 3. Converts DataArray into pandas DataFrame
    # 4. .reset_index() converts indices into columns (into spreadsheet form basically)
    # OR more complexly, stacks the dimensions (time, lat, lon) into a single index 
    df = da.to_dataframe().reset_index()

    # 5. Rename data columns for clarity
    df = df.rename(columns={variable: "moisture"})

    # 6. Drop rows with missing moisture values
    df = df.dropna(subset=["moisture"])

    # 7. Return the DataFrame!
    return df

if __name__ == "__main__":
    path_to_file = "data/C3S-SOILMOISTURE-L3S-SSMV-COMBINED-DAILY-20230101000000-TCDR-v202312.0.0.nc"
    df = netcdf_to_pandas(path_to_file, "sm")
    print (df.head())


# Tomorrow, 
# Try not just df.head, maybe printing more results
# Check runtime
# maybe try auto closing dataset to improve runtme?

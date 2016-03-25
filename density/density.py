import pandas as pd
import seaborn as sns
from pandas.tools.plotting import autocorrelation_plot

sns.set_style('darkgrid')

_start = None
_end = "20150915"

df = pd.read_csv('data/data.csv') \
       .assign(dump_time=lambda df: pd.to_datetime(df['dump_time'])) \
       .set_index("dump_time") \
       .fillna("Butler") \
       .assign(parent_name=lambda df: df.parent_name.astype("category")) \
       .assign(group_name=lambda df: df.group_name.astype("category"))

buildings = df.groupby(df.parent_name).group_name.unique() \
              .map(set) \
              .to_dict()

group_names = {"M": "Monthly", "H": "Hourly", "W": "Weekly", "D": "Daily"}


def get_series(building, group=None, start=_start, end=_end):
    floors = buildings[building]
    floor_data = df.loc[df.group_name.isin(floors),
                        ["group_name", "client_count"]] \
                   .loc[start: end] \
                   .pivot(columns="group_name", values="client_count")

    if group is not None:
        floor_data = floor_data.resample(group, how='sum')

    return floor_data


def building_plot(building, group=None, start=_start, end=_end):
    floor_data = get_series(building, group=group, start=start, end=end)
    ax = floor_data.plot.line(figsize=(10, 7))
    ax.set_xlabel("Date")
    ax.set_ylabel("Device Count")
    ax.set_title("{} {} Device Counts".format(group_names.get(group, ""),
                                              building))


def autocorrelation(building, floor, group=None, start=_start, end=_end):
    floor_data = get_series(building, group=group, start=start, end=end)
    series = floor_data[floor]
    autocorrelation_plot(series)

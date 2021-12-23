from typing import Sequence

import pandas as pd
from biopsykit.protocols import MIST
from biopsykit.utils.datatype_helper import SubjectConditionDataFrame


def reshape_hr_data(mist: MIST) -> pd.DataFrame:
    hr_mean_data = mist.hr_results["hr_mean"]
    hr_mean_data.columns = ["HR"]
    hr_mean_data_normalized = mist.hr_results["hr_mean_normalized"]
    hr_mean_data_normalized.columns = ["HR_Norm"]

    hr_data = pd.concat([hr_mean_data, hr_mean_data_normalized], axis=1)
    hr_data.columns.name = "type"
    hr_data = pd.DataFrame(hr_data.stack(), columns=["data"])
    return hr_data


def reshape_hrv_data(mist: MIST, hrv_columns: Sequence[str]) -> pd.DataFrame:
    hrv_phases_data = mist.hrv_results["hrv_phases"]
    hrv_subphases_data = mist.hrv_results["hrv_subphases"]

    hrv_phases_data = hrv_phases_data[hrv_columns]
    hrv_subphases_data = hrv_subphases_data[hrv_columns]

    hrv_phases_data = pd.concat({"Total": hrv_phases_data}, names=["subphase"])
    hrv_phases_data = hrv_phases_data.reorder_levels(["condition", "subject", "phase", "subphase"])

    hrv_phases_data.columns.name = "type"
    hrv_subphases_data.columns.name = "type"

    hrv_data = pd.concat([hrv_phases_data, hrv_subphases_data])
    hrv_data = pd.DataFrame(hrv_data.stack(), columns=["data"])
    return hrv_data


def reshape_time_above_bl_glo(mist: MIST) -> pd.DataFrame:
    hr_above_bl = mist.hr_above_baseline_results["hr_above_bl_glo"]
    hr_above_bl.columns = ["HR"]
    hrv_above_bl = mist.hrv_above_baseline_results["hrv_above_bl_glo"]
    above_bl = pd.concat([hr_above_bl, hrv_above_bl], axis=1)
    above_bl.columns.name = "type"
    above_bl = pd.DataFrame(above_bl.stack(), columns=["data"])
    return above_bl


def reshape_cft_params(cft_params: pd.DataFrame, condition_list: SubjectConditionDataFrame) -> pd.DataFrame:
    cft_params_long = pd.concat({"Total": cft_params}, names=["subphase"])
    cft_params_long = cft_params_long.reorder_levels(cft_params_long.index.names[1:] + [cft_params_long.index.names[0]])
    cft_params_long = cft_params_long.join(condition_list.set_index("condition", append=True))
    cft_params_long = cft_params_long.reorder_levels(
        [cft_params_long.index.names[-1]] + cft_params_long.index.names[:-1]
    )
    cft_params_long.columns.name = "type"
    cft_params_long = pd.DataFrame(cft_params_long.stack(), columns=["data"])
    cft_params_long = cft_params_long.drop("onset", level="type")
    cft_params_long = cft_params_long.drop("peak_brady", level="type")
    return cft_params_long

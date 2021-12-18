__all__ = ["percent_above_baseline_hr", "percent_above_baseline_hrv", "cft_parameter_per_phase"]

from typing import Dict, Optional, Sequence

from tqdm.auto import tqdm

import pandas as pd
from biopsykit.protocols import CFT
from biopsykit.utils.data_processing import select_dict_phases, split_dict_into_subphases, normalize_to_phase
from biopsykit.utils.datatype_helper import SubjectDataDict


def percent_above_baseline_hr(subject_data_dict: SubjectDataDict) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
    subject_data_dict = normalize_to_phase(subject_data_dict, "Pre")
    # select only MIST phases to split into subphases
    subject_data_dict = select_dict_phases(subject_data_dict, ["MIST1", "MIST2", "MIST3"])
    subject_data_dict = split_dict_into_subphases(
        subject_data_dict, subphases={"BL": 60, "RP_CFI": 120, "AT": 240, "FB": 0}
    )

    subject_dict_result = {}
    for subject_id, hr_data_dict in tqdm(list(subject_data_dict.items())):
        dict_hr = {}

        for phase, dict_hr_phase in hr_data_dict.items():
            dict_hr.setdefault(phase, {})
            for subphase, df_hr in dict_hr_phase.items():
                hr_above_bl = (df_hr > 0).sum() / len(df_hr) * 100
                dict_hr[phase][subphase] = hr_above_bl

        subject_dict_result[subject_id] = dict_hr
    return subject_dict_result


def percent_above_baseline_hrv(
    subject_data_dict: SubjectDataDict, hrv_columns: Optional[Sequence[str]] = None
) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
    # select only baseline
    subject_data_dict_bl = select_dict_phases(subject_data_dict, ["Pre"])
    # select all only MIST phases to split into subphases
    subject_data_dict = select_dict_phases(subject_data_dict, ["MIST1", "MIST2", "MIST3"])
    subject_data_dict = split_dict_into_subphases(
        subject_data_dict, subphases={"BL": 60, "RP_CFI": 120, "AT": 240, "FB": 0}
    )

    subject_dict_result = {}
    for subject_id, hrv_data_dict in tqdm(list(subject_data_dict.items())):
        dict_hrv = {}

        hrv_baseline = subject_data_dict_bl[subject_id]["Pre"]
        if hrv_columns is None:
            hrv_columns = hrv_baseline.columns
        hrv_baseline = hrv_baseline[hrv_columns]

        for phase, dict_hrv_phase in hrv_data_dict.items():
            dict_hrv.setdefault(phase, {})
            for subphase, df_hrv in dict_hrv_phase.items():
                df_hrv = df_hrv[hrv_columns]
                hrv_above_bl = (df_hrv > hrv_baseline.mean()).sum() / len(df_hrv) * 100
                dict_hrv[phase][subphase] = hrv_above_bl

        subject_dict_result[subject_id] = dict_hrv
    return subject_dict_result


def cft_parameter_per_phase(
    subject_data_dict: SubjectDataDict, cft_subject_list: Sequence[str]
) -> Dict[str, Dict[str, pd.DataFrame]]:
    subject_dict_result = {}

    # select all only MIST phases to split into subphases
    subject_data_dict = select_dict_phases(subject_data_dict, ["MIST1", "MIST2", "MIST3"])

    for subject_id, hr_data_dict in tqdm(list(subject_data_dict.items())):
        if subject_id not in cft_subject_list:
            continue
        dict_cft_params = {}
        for phase, hr_data_phase in hr_data_dict.items():
            cft = CFT(structure={"Baseline": 60, "CFT": 120})
            dict_cft_params[phase] = cft.compute_cft_parameter(hr_data_phase)
        subject_dict_result[subject_id] = dict_cft_params

    return subject_dict_result

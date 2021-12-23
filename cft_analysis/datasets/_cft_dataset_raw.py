import itertools
from functools import cached_property, lru_cache
from typing import Dict, Optional, Sequence, Union

import biopsykit as bp
import pandas as pd
from biopsykit.io import load_long_format_csv, load_questionnaire_data
from biopsykit.utils.dataframe_handling import multi_xs
from biopsykit.utils.datatype_helper import SubjectConditionDataFrame
from biopsykit.utils.file_handling import mkdirs
from tpcp import Dataset

from cft_analysis._types import path_t
from cft_analysis.datasets.helper import load_ecg_raw_data_folder

_cached_load_ecg_raw_data_folder = lru_cache(maxsize=5)(load_ecg_raw_data_folder)


class CftDatasetRaw(Dataset):

    base_path: path_t
    use_cache: bool
    _sampling_rate: float = 256.0
    phases: Sequence[str] = None

    def __init__(
        self,
        base_path: path_t,
        groupby_cols: Optional[Sequence[str]] = None,
        subset_index: Optional[Sequence[str]] = None,
        use_cache: Optional[bool] = True,
    ):
        super().__init__(groupby_cols=groupby_cols, subset_index=subset_index)
        # ensure pathlib
        self.base_path = base_path
        self.use_cache = use_cache
        self.phases = ["Pre", "MIST1", "MIST2", "MIST3", "Post"]

    def create_index(self) -> pd.DataFrame:
        condition_list = bp.io.load_subject_condition_list(self.base_path.joinpath("condition_list.csv"))
        condition_list = condition_list.reset_index()

        phase_list = itertools.product(condition_list["subject"].unique(), self.phases)
        phase_list = pd.DataFrame(phase_list, columns=["subject", "phase"])
        return condition_list.merge(phase_list)

    @property
    def sampling_rate(self) -> float:
        return self._sampling_rate

    @cached_property
    def ecg(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        if any([self.is_single(None), self.is_single(["subject", "condition"]), self.is_single(["subject"])]):
            subject_id = self.index["subject"][0]
            phase = list(self.index["phase"].unique())
            return self._load_ecg(subject_id, phase=phase)

        raise ValueError(
            "Data can only be accessed for a single participant or a single phase "
            "of one single participant in the subset"
        )

    def _load_ecg(self, subject_id: str, phase: Sequence[str]) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        if self.use_cache:
            data_dict = _cached_load_ecg_raw_data_folder(
                self.base_path,
                subject_id,
                phase_names=tuple(self.phases),
                selected_phases=tuple(phase),
                datastreams="ecg",
            )
        else:
            data_dict = load_ecg_raw_data_folder(
                self.base_path, subject_id, phases=self.phases, selected_phases=phase, datastreams="ecg"
            )
        if self.is_single(None):
            return data_dict[phase[0]]
        return data_dict

    @property
    def questionnaire(self):
        if self.is_single(None):
            raise ValueError("questionnaire data can not be accessed for individual phases!")
        return self._load_questionnaire_data()

    @property
    def cortisol(self) -> pd.DataFrame:
        return self._load_saliva_data("cortisol")

    @property
    def subject_dirs(self) -> Sequence[path_t]:
        return bp.utils.file_handling.get_subject_dirs(self.base_path.joinpath("ecg"), r"Vp\w+")

    @property
    def condition_list(self) -> SubjectConditionDataFrame:
        condition_df = self.index[["subject", "condition"]]
        condition_df = condition_df.drop_duplicates()
        condition_df = condition_df.set_index("subject")
        return condition_df

    def _load_questionnaire_data(self) -> pd.DataFrame:
        data_path = self.base_path.joinpath("questionnaire/cleaned/questionnaire_data_cleaned.xlsx")

        data = load_questionnaire_data(data_path)
        subject_ids = self.index["subject"].unique()
        data = data.loc[subject_ids]

        condition = self.index["condition"].unique()
        return multi_xs(data, condition, level="condition")

    def _load_saliva_data(self, saliva_type: str) -> pd.DataFrame:
        if self.is_single(["subject", "condition", "phase"]):
            raise ValueError(f"{saliva_type} data can not be accessed for individual phases!")
        data_path = self.base_path.joinpath(f"saliva/processed/{saliva_type}_samples.csv")
        data = load_long_format_csv(data_path)

        subject_ids = self.index["subject"].unique()
        conditions = self.index["condition"].unique()
        return multi_xs(multi_xs(data, subject_ids, level="subject"), conditions, level="condition")

    def setup_export_paths(self) -> Dict[str, path_t]:
        if not self.is_single("subject"):
            print("Only supported for a single participant!")
        subject_id = self.index["subject"][0]
        ecg_path_proc = self.base_path.joinpath(f"ecg/{subject_id}/processed")
        mkdirs(ecg_path_proc)

        hr_result_filename = ecg_path_proc.joinpath("hr_result_{}.xlsx".format(subject_id))
        rpeaks_result_filename = ecg_path_proc.joinpath("rpeaks_result_{}.xlsx".format(subject_id))
        hrv_cont_filename = ecg_path_proc.joinpath("hrv_continuous_{}.xlsx".format(subject_id))
        return {"hr_result": hr_result_filename, "rpeaks_result": rpeaks_result_filename, "hrv_cont": hrv_cont_filename}

import itertools
from functools import cached_property, lru_cache
from typing import Tuple, Optional, Sequence, Union, Dict

import pandas as pd

import biopsykit as bp
from tpcp import Dataset

from cft_analysis._types import path_t
from cft_analysis.datasets.helper import load_ecg_raw_data_folder

_cached_load_ecg_raw_data_folder = lru_cache(maxsize=4)(load_ecg_raw_data_folder)


class CftDataset(Dataset):

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
            "Data can only be accessed for a single participant or a single phase of one single in the subset"
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
                self.base_path, subject_id, phase_names=self.phases, selected_phases=phase, datastreams="ecg"
            )
        if self.is_single(None):
            return data_dict[phase[0]]
        return data_dict

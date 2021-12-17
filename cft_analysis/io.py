import warnings
from pathlib import Path
from typing import Optional, Sequence, Tuple, Dict

from biopsykit.io import load_pandas_dict_excel
from tqdm.auto import tqdm

import pandas as pd
from nilspodlib.legacy import CorruptedPackageWarning, LegacyWarning

from biopsykit.utils.datatype_helper import SubjectDataDict
from biopsykit.io.nilspod import load_dataset_nilspod, load_csv_nilspod

from cft_analysis._types import path_t

__all__ = ["load_ecg_raw_data_folder", "load_subject_data_dicts"]


def load_ecg_raw_data_folder(
    folder_path: path_t, phase_names: Optional[Sequence[str]] = None
) -> Tuple[Dict[str, pd.DataFrame], float]:
    """Load all NilsPod datasets from one folder, convert them into dataframes, and combine them into a dictionary.

    This function can for example be used when single NilsPod sessions (datasets) were recorded
    for different study phases.

    ..note:: This function is different from the function :func:`biopsykit.io.nilspod.load_folder_nilspod` in the way
    that is does not only scan for .bin files, but also for .csv files containing NilsPod data. Due to data recording
    mistakes during the study some files were accidentially recorded as .csv files instead of .bin files,
    which will be accounted for in this function.

    Parameters
    ----------
    folder_path : :class:`~pathlib.Path` or str, optional
        folder path to files
    phase_names: list, optional
        list of phase names corresponding to the files in the folder. Must match the number of recordings.
        If ``None`` phase names will be named ``Part{1-x}``. Default: ``None``

    Returns
    -------
    dataset_dict : dict
        dictionary with phase names as keys and pandas dataframes with sensor recordings as values
    fs : float
        sampling rate of sensor recordings

    Raises
    ------
    ValueError
        if ``folder_path`` does not contain any NilsPod files, the number of phases does not match the number of
        datasets in the folder, or if the sampling rates of the files in the folder are not the same

    """
    # ensure pathlib
    folder_path = Path(folder_path)
    # look for all NilsPod binary and csv files in the folder
    dataset_list = sorted(list(folder_path.glob("*.bin")) + list(sorted(folder_path.glob("*.csv"))))

    if len(dataset_list) == 0:
        raise ValueError("No NilsPod files found in folder!")
    if phase_names is None:
        phase_names = ["Part{}".format(i) for i in range(len(dataset_list))]

    if len(phase_names) != len(dataset_list):
        raise ValueError("Number of phases does not match number of datasets in the folder!")

    # ignore legacy and package warnings from nilspodlib since it comes from a firmware bug that we can ignore when
    # cutting away the last second of the data
    warnings.filterwarnings("ignore", category=CorruptedPackageWarning)
    warnings.filterwarnings("ignore", category=LegacyWarning)
    dataset_list = [
        load_dataset_nilspod(file_path=dataset_path, handle_counter_inconsistency="ignore", legacy_support="resolve")
        if dataset_path.suffix == ".bin"
        else load_csv_nilspod(file_path=dataset_path)
        for dataset_path in dataset_list
    ]
    # remove the last second of the dataframe
    dataset_list = [(data.iloc[: -int(fs)], fs) for (data, fs) in dataset_list]

    # check if sampling rate is equal for all datasets in folder
    fs_list = [fs for df, fs in dataset_list]

    if len(set(fs_list)) > 1:
        raise ValueError("Datasets in the sessions have different sampling rates! Got: {}.".format(fs_list))
    fs = fs_list[0]

    dataset_dict = {phase: df for phase, (df, fs) in zip(phase_names, dataset_list)}
    return dataset_dict, fs


def load_subject_data_dicts(subject_dirs: Sequence[path_t]) -> Tuple[SubjectDataDict, SubjectDataDict]:
    subject_data_dict_hr = {}
    subject_data_dict_rpeaks = {}

    for subject_dir in tqdm(subject_dirs):
        subject_id = subject_dir.name

        hr_path = subject_dir.joinpath("processed")
        hr_filename = hr_path.joinpath("hr_result_{}.xlsx".format(subject_id))
        rpeaks_filename = hr_path.joinpath("rpeaks_result_{}.xlsx".format(subject_id))

        hr_dict = load_pandas_dict_excel(hr_filename)
        rpeaks_dict = load_pandas_dict_excel(rpeaks_filename)

        subject_data_dict_hr[subject_id] = hr_dict
        subject_data_dict_rpeaks[subject_id] = rpeaks_dict

    return subject_data_dict_hr, subject_data_dict_rpeaks


def load_subject_continuous_hrv_data(subject_dirs: Sequence[path_t]) -> Dict[str, Dict[str, pd.DataFrame]]:
    subject_data_dict_hrv = {}

    for subject_dir in tqdm(subject_dirs):
        subject_id = subject_dir.name
        hr_path = subject_dir.joinpath("processed")

        subject_data_dict_hrv[subject_id] = load_pandas_dict_excel(
            hr_path.joinpath("hrv_continuous_{}.xlsx".format(subject_id)), index_col=0
        )
    return subject_data_dict_hrv

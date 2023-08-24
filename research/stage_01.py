# Data ingestion stage

## Defining DataIngestionConfig - Option 1
import os
from collections import namedtuple

os.getcwd()

os.chdir("../")


DataIngestionConfig = namedtuple(
    "DataIngestionConfig",
    [
        "root_dir",
        "source_URL",
        "local_data_file",
        "unzip_dir",
    ],
)

## Defining DataIngestionConfig - Option 2
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    source_URL: str
    local_data_file: Path
    unzip_dir: Path


from cnn_classifier.constants import CONGIG_FILEPATH, PARAMS_FILEPATH
from cnn_classifier.utils import read_yaml, create_directories


class ConfigurationManager:
    def __init__(
        self,
        config_filepath=CONGIG_FILEPATH,
        params_filepath=PARAMS_FILEPATH,
    ):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=config.root_dir,
            source_URL=config.source_URL,
            local_data_file=config.local_data_file,
            unzip_dir=config.unzip_dir,
        )

        return data_ingestion_config


import urllib.request as request
from zipfile import ZipFile


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        if not os.path.exists(self.config.local_data_file):
            filename, headers = request.urlretrieve(
                url=self.config.source_URL,
                filename=self.config.local_data_file,
            )

    def _get_updated_list_of_files(self, list_of_files):
        return [
            f
            for f in list_of_files
            if f.endswith(".jpg") and ("Cat" in f or "Dog" in f)
        ]

    def _preprocess(self, zf: ZipFile, f: str, working_dir: str):
        target_filepath = os.path.join(working_dir, f)
        if not os.path.exists(target_filepath):
            zf.extract(f, working_dir)

        if os.path.getsize(target_filepath) == 0:
            os.remove(target_filepath)

    def unzip_and_clean(self):
        with ZipFile(file=self.config.local_data_file, mode="r") as zf:
            list_of_files = zf.namelist()
            updated_list_of_files = self._get_updated_list_of_files(list_of_files)
            for f in updated_list_of_files:
                self._preprocess(zf, f, self.config.unzip_dir)


try:
    config = ConfigurationManager()
    data_ingestion_config = config.get_data_ingestion_config()
    data_ingestion = DataIngestion(config=data_ingestion_config)
    data_ingestion.download_file()
    data_ingestion.unzip_and_clean()
except Exception as e:
    raise e

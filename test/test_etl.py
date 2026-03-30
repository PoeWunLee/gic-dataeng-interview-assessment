import pytest
from src.etl import PipelineRun, PipelineStatus
from utils.file_utils import get_paths
import sqlite3
from pathlib import Path


@pytest.fixture
def make_cnxn_str(tmp_path:Path):
    return tmp_path / "test.db"

@pytest.fixture
def make_connection(make_cnxn_str:Path):
    """Fixture for temporary testing DB"""
    conn=sqlite3.connect(make_cnxn_str)
    yield conn
    conn.commit()
    conn.close()

@pytest.fixture
def make_paths(tmp_path:Path):
    return get_paths(tmp_path)

@pytest.fixture
def make_pipeline(input_args:dict[str,bool]):
    return PipelineRun(input_args['init'], input_args['extract'], input_args['load'], input_args['analyse'])

@pytest.fixture
def make_results(output_count:dict[str,int]):
    status = PipelineStatus()
    status.extracted_files=output_count["extract"]
    status.loaded_files=output_count["load"]
    status.analysed_files=output_count["analyse"]

    return status

@pytest.mark.parametrize(
    "input_args,output_count",
    [
        ({"init":False, "extract":False, "load":False, "analyse":False}, {"init":0, "extract":0, "load":0, "analyse":0})
    ]
)
def test_pipeline_func_correct(input_args,output_count, tmp_path,make_pipeline, make_results, make_cnxn_str,make_connection, make_paths):
    #arrange
    pipeline=make_pipeline
    expected_results=make_results
    paths=make_paths
    cnxn_str = make_cnxn_str
    make_connection

    #act
    status = pipeline.run(path=paths, cnxn_str=cnxn_str)

    #assert
    assert status.extracted_files == expected_results.extracted_files
    assert status.loaded_files == expected_results.loaded_files
    assert status.analysed_files == expected_results.analysed_files



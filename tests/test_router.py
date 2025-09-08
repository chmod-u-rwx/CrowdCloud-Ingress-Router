import pytest
from unittest.mock import patch
from src.router import Router
from tests.dataclasses.jobcache import JobCache 


@pytest.fixture
def sample_workers():
    return [
        {
            "worker_id": "w1",
            "master_id": "m1",
            "cpu": 4,
            "memory": 16,
            "job_slot": 2,
            "status": "active",
            "code_runtime": 1.2,
            "job_cache": []
        },
        {
            "worker_id": "w2",
            "master_id": "m1",
            "cpu": 8,
            "memory": 8,
            "job_slot": 1,
            "status": "active",
            "code_runtime": 2.0,
            "job_cache": []
        },
    ]


def make_job(job_id: str, reward: float = 0.0):
    return {
        "job_id": job_id,
        "repo_link": "",
        "path": "",
        "query_params": {},
        "body": None,
        "headers": {},
        "reward": reward,
    }


def test_update_worker_data_valid(sample_workers):
    router = Router()
    router.update_worker_data(sample_workers)
    assert len(router.workers) == 2


def test_update_worker_data_missing_fields(sample_workers):
    router = Router()
    bad_worker = {"worker_id": "w3"}
    router.update_worker_data(sample_workers + [bad_worker])
    assert all("worker_id" in w for w in router.workers)
    assert all("cpu" in w for w in router.workers)


def test_update_worker_data_invalid_types(sample_workers):
    router = Router()
    bad_worker = sample_workers[0].copy()
    bad_worker["cpu"] = "not_a_number"
    router.update_worker_data([bad_worker])
    assert len(router.workers) == 0


def test_select_worker_job_cache_priority(sample_workers):
    router = Router()
    sample_workers[0]["job_cache"] = [make_job("job1", 10)]
    sample_workers[1]["job_cache"] = [make_job("job1", 5)]
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("job1"))
    assert chosen["worker_id"] == "w1"


def test_select_worker_job_cache_tie(sample_workers):
    router = Router()
    sample_workers[0]["job_cache"] = [make_job("job1", 10)]
    sample_workers[1]["job_cache"] = [make_job("job1", 10)]
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("job1"))
    assert chosen["worker_id"] in ["w1", "w2"]


def test_select_worker_invalid_job_cache(sample_workers):
    router = Router()
    sample_workers[0]["job_cache"] = [{"job_id": "job1"}]  # missing reward
    router.update_worker_data(sample_workers)

    with pytest.raises(KeyError, match="missing reward key"):
        router.select_worker(make_job("job1"))


def test_select_worker_hardware_scoring(sample_workers):
    router = Router()
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("jobX"))  # no cache
    assert chosen["worker_id"] == "w2"  # w2 has stronger CPU


def test_select_worker_hardware_tie(sample_workers):
    router = Router()
    sample_workers[0]["cpu"] = 4
    sample_workers[1]["cpu"] = 4
    sample_workers[0]["memory"] = 8
    sample_workers[1]["memory"] = 8
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("jobX"))
    assert chosen["worker_id"] in ["w1", "w2"]


@patch("random.random", return_value=0.05)
def test_select_worker_epsilon_exploration(mock_rand, sample_workers):
    router = Router(epsilon=0.1)
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("jobX"))
    assert chosen["worker_id"] in ["w1", "w2"]


@patch("random.random", return_value=0.9)
def test_select_worker_epsilon_exploitation(mock_rand, sample_workers):
    router = Router(epsilon=0.1)
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("jobX"))
    assert chosen["worker_id"] == "w2"


def test_select_worker_always_explore(sample_workers):
    router = Router(epsilon=1.0)
    router.update_worker_data(sample_workers)

    results = {router.select_worker(make_job("jobX"))["worker_id"] for _ in range(10)}
    assert results == {"w1", "w2"}


def test_select_worker_always_exploit(sample_workers):
    router = Router(epsilon=0.0)
    router.update_worker_data(sample_workers)

    for _ in range(10):
        chosen = router.select_worker(make_job("jobX"))
        assert chosen["worker_id"] == "w2"


def test_select_worker_inactive_worker(sample_workers):
    router = Router()
    sample_workers[0]["status"] = "inactive"
    router.update_worker_data(sample_workers)

    chosen = router.select_worker(make_job("jobX"))
    assert chosen["worker_id"] == "w2"


def test_select_worker_empty_list():
    router = Router()
    with pytest.raises(ValueError):
        router.select_worker(make_job("jobX"))

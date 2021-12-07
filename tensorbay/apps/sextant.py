#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Interact with sextant app at graviti marketplace."""

import time
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import urljoin

from tensorbay.client.lazy import PagingList
from tensorbay.client.requests import Client
from tensorbay.exception import ResourceNotExistError


class Evaluation:
    """This class defines :class:`Evaluation`.

    Arguments:
        evaluation_id: Evaluation ID.
        created_at: Created time of the evaluation.
        benchmark: The :class:`Benchmark`.

    """

    def __init__(self, evaluation_id: str, created_at: int, benchmark: "Benchmark") -> None:
        self.evaluation_id = evaluation_id
        self.benchmark = benchmark
        self.created_at = created_at

    def __repr__(self) -> str:
        read_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.created_at))
        return f"{self.__class__.__name__} createdAt: {read_time}"

    def get_result(self) -> Dict[str, Any]:
        """Get the result of the evaluation.

        Returns:
            The result dict of the evaluation.

        """
        return self.benchmark.sextant.open_api_do(  # type: ignore[no-any-return]
            "GET",
            f"benchmarks/{self.benchmark.benchmark_id}/evaluations/{self.evaluation_id}/results",
            "",
        ).json()

    # def get_status(self) -> str:
    #     """Get the status of the evaluation.

    #     Return:
    #         One of "success", "fail" or "processing".

    #     """


class Benchmark:  # pylint: disable=too-many-instance-attributes
    """This class defines :class:`Benchmark`.

    Arguments:
        name: Name of the Benchmark.
        dataset_id: ID of the dataset on which this benchmark based.
        commit_id: ID of the commit which is used as the evaluation benchmark.
        benchmark_id: Benchmark ID.
        sextant: The :class:`SextantClient`.
        categories: The needed evaluation categories, if not given, all categories will be used.
        iou_threshold: The IoU threshold.
        customized_metrics: Https url of the github repository.

    """

    def __init__(
        self,
        name: str,
        benchmark_id: str,
        sextant: "Sextant",
        *,
        dataset_id: Optional[str] = None,
        commit_id: Optional[str] = None,
        categories: Optional[List[str]] = None,
        iou_threshold: Optional[float] = None,
        customized_metrics: Optional[str] = None,
    ) -> None:
        self.name = name
        self.dataset_id = dataset_id
        self.benchmark_id = benchmark_id
        self.commit_id = commit_id
        self.sextant = sextant
        self.categories = categories
        self.iou_threshold = iou_threshold
        self.customized_metrics = customized_metrics

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'

    def _generate_evaluations(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[Evaluation, None, int]:

        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        response = self.sextant.open_api_do(
            "GET", f"benchmarks/{self.benchmark_id}/evaluations", "", params=params
        ).json()

        for evaluation in response["evaluations"]:
            yield Evaluation(evaluation["evaluationId"], evaluation["createdAt"], self)

        return response["totalCount"]  # type: ignore[no-any-return]

    def create_evaluation(self, dataset_id: str, commit_id: str) -> Evaluation:
        """Create an evaluation task.

        Arguments:
            dataset_id: Id of the needed evaluation dataset.
            commit_id: Id of the needed commit.

        Returns:
            The created evaluation instance.

        """
        post_data = {"datasetId": dataset_id, "commitId": commit_id}
        evaluation_id = self.sextant.open_api_do(
            "POST", f"benchmarks/{self.benchmark_id}/evaluations", "", json=post_data
        ).json()["evaluationId"]
        return Evaluation(evaluation_id, int(time.time()), self)

    def list_evaluations(self) -> PagingList[Evaluation]:
        """List all evaluations.

        Returns:
            A list of evaluations.

        """
        return PagingList(self._generate_evaluations, 128)


class Sextant(Client):
    """This class defines :class:`Sextant`.

    Arguments:
        access_key: User's access key.
        url: The URL of the graviti gas website.

    """

    def __init__(self, access_key: str, url: str = "") -> None:
        super().__init__(access_key, url)
        self._open_api = urljoin(self.gateway_url, "apps-sextant/v1/")

    def _generate_benmarks(
        self, offset: int = 0, limit: int = 128
    ) -> Generator[Benchmark, None, int]:

        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        response = self.open_api_do("GET", "benchmarks", "", params=params).json()

        for benchmark in response["benchmarks"]:
            yield Benchmark(benchmark["name"], benchmark["benchmarkId"], self)

        return response["totalCount"]  # type: ignore[no-any-return]

    # def create_benchmark(
    #     self,
    #     name: str,
    #     dataset_id: str,
    #     commit_id: str,
    #     *,
    #     categories: Optional[List[str]] = None,
    #     iou_threshold: Optional[float] = None,
    #     customized_metrics: Optional[str] = None,
    # ) -> Benchmark:
    #     """Create a benchmark with the given parameters.

    #     Arguments:
    #         name: Name of the Benchmark.
    #         dataset_id: ID of the dataset on which this benchmark based.
    #         commit_id: ID of the commit which used as the evaluation benchmark.
    #         categories: The needed evaluation categories, if not given,
    #                   all categories will be used.
    #         iou_threshold: The IoU threshold.
    #         customized_metrics: Https url of the github repository.

    #     Raises:
    #         ValueError: When iou_threshold and customized_metrics both given or both not given.

    #     """

    def list_benchmarks(self) -> PagingList[Benchmark]:
        """List all benchmarks.

        Returns:
            The list of Benchmark instances.

        """
        return PagingList(self._generate_benmarks, 128)

    def get_benchmark(self, name: str) -> Benchmark:
        """Get a benchmark instance by name.

        Arguments:
            name: Name of the Benchmark.

        Returns:
            The Benchmark instance with the given name.

        Raises:
            ResourceNotExistError: When the required benchmark does not exist.

        """
        for benchmark in self.list_benchmarks():
            if benchmark.name == name:
                return benchmark

        raise ResourceNotExistError(resource="benchmark", identification=name)

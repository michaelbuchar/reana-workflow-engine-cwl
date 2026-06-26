# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-CWL tests."""

from types import SimpleNamespace

import pytest

from reana_workflow_engine_cwl.cwl_reana import ReanaPipelineJob


@pytest.mark.parametrize(
    "step_secret_names,workflow_secret_names,expected_secret_names",
    [
        (None, None, None),
        (None, ["global"], ["global"]),
        ([], ["global"], []),
        (["local"], ["global"], ["local"]),
    ],
)
def test_create_task_msg_secret_names_resolution(
    step_secret_names, workflow_secret_names, expected_secret_names
):
    """Step hints should override or inherit workflow-global secret_names."""
    job = ReanaPipelineJob.__new__(ReanaPipelineJob)
    job.name = "fit"
    job.environment = {"HOME": "/tmp/outdir"}
    job.volumes = []
    job.command_line = ["echo", "hello"]
    job.stdin = None
    job.stdout = None
    job.stderr = None
    job.outdir = "/tmp/outdir"
    job.builder = SimpleNamespace(outdir="/tmp/outdir", bindings=[])
    job.workflow_resources = (
        {"secret_names": workflow_secret_names}
        if workflow_secret_names is not None
        else {}
    )
    job.hints = []
    if step_secret_names is not None:
        job.hints.append({"secret_names": step_secret_names})
    job.get_requirement = lambda name: (
        ({"dockerPull": "docker.io/library/busybox"}, None)
        if name == "DockerRequirement"
        else (None, None)
    )

    create_body = job.create_task_msg("/tmp/workspace", "workflow-uuid")

    assert create_body["secret_names"] == expected_secret_names

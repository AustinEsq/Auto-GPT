import pytest
from pytest_mock import MockerFixture

from autogpt.agent import Agent
from autogpt.commands.file_operations import read_file, write_to_file
from tests.challenges.challenge_decorator.challenge_decorator import challenge
from tests.challenges.utils import (
    generate_noise,
    get_workspace_path_from_agent,
    run_interaction_loop,
)

NOISE = 1000
OUTPUT_LOCATION = "output.txt"


@challenge()
def test_memory_challenge_b(
    memory_management_agent: Agent,
    patched_api_requestor: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
    level_to_run: int,
    challenge_name: str,
) -> None:
    """
    The agent reads a series of files, each containing a task_id and noise. After reading 'n' files,
    the agent must write all the task_ids into a new file, filtering out the noise.

    Args:
        memory_management_agent (Agent)
        patched_api_requestor (MockerFixture)
        monkeypatch (pytest.MonkeyPatch)
        level_to_run (int)
    """
    task_ids = [str(i * 1111) for i in range(1, level_to_run + 1)]
    create_instructions_files(memory_management_agent, level_to_run, task_ids)

    run_interaction_loop(
        monkeypatch,
        memory_management_agent,
        level_to_run + 2,
        challenge_name,
        level_to_run,
    )

    file_path = get_workspace_path_from_agent(memory_management_agent, OUTPUT_LOCATION)
    content = read_file(file_path, memory_management_agent)
    for task_id in task_ids:
        assert task_id in content, f"Expected the file to contain {task_id}"


def create_instructions_files(
    memory_management_agent: Agent,
    level: int,
    task_ids: list,
    base_filename: str = "instructions_",
) -> None:
    """
    Creates a series of instructions files for the memory challenge.
    Args:
        level:
        memory_management_agent (Agent)
        num_files (int)
        task_ids (list)
        base_filename (str, optional)
    """
    for i in range(1, level + 1):
        content = generate_content(i, task_ids, base_filename, level)
        file_name = f"{base_filename}{i}.txt"
        file_path = get_workspace_path_from_agent(memory_management_agent, file_name)

        write_to_file(file_path, content, memory_management_agent)


def generate_content(index: int, task_ids: list, base_filename: str, level: int) -> str:
    """
    Args:
        index: int
        task_ids: list
        base_filename: str
        num_files: int

    Returns: str
    """
    task_id = task_ids[index - 1]
    noise = generate_noise(NOISE)
    if index != level:
        if level == 1:
            return f"{noise}\nThe current task_id is {task_id}.\n{noise}\nWrite all the task_ids into the file output.txt. The file has not been created yet. After that, use the task_complete command."
        return f"{noise}\nThe current task_id is {task_id}.\n{noise}\nRead the file {base_filename}{index + 1}.txt using the read_file command."
    return f"{noise}\nThis task_id is {task_id}\n{noise}\nWrite all the task_ids into the file output.txt. The file has not been created yet. After that, use the task_complete command.\n"

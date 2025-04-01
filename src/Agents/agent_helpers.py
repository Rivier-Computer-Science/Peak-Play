
def concatente_task_outputs(result):
    task_outputs = result.tasks_output
    raw_outputs = [output.raw for output in reversed(task_outputs)]
    return " ".join(raw_outputs) 


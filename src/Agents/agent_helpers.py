
def concatente_task_outputs(result):
    task_outputs = result.tasks_output
    # Summary is last output
    if task_outputs:
        last_output = task_outputs.pop()
    raw_outputs = [output.raw for output in task_outputs]
    return last_output.join(raw_outputs) 



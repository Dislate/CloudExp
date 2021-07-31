def get_task(chapter):
    task_list = chapter.task_list
    try:
        task_list[0]
    except:
        return ''
    else:
        return task_list

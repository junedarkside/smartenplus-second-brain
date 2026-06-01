# Django Pattern — Async AI/LLM Calls via Celery

## Summary

Synchronous LLM API calls in Django views block WSGI workers for 5–20s. At 5 concurrent requests, all workers stall and the entire app degrades. Pattern: view returns `task_id` immediately, Celery task handles the AI call, frontend polls for result.

## Problem

```python
# WRONG — blocks WSGI worker for 5-20 seconds
@action(detail=False, methods=['post'])
def import_pdf(self, request):
    result = call_llm_api(request.data['text'])  # 5-20s blocking call
    return Response(result)
```

With 4 WSGI workers (typical Django/gunicorn config), 4 concurrent import requests = 0 workers available for all other requests. Dashboard freezes for all users.

## Pattern

```python
# CORRECT — return task_id immediately
@action(detail=False, methods=['post'])
def import_pdf(self, request):
    task = process_import_async.delay(request.data['text'], request.user.id)
    return Response({'task_id': task.id}, status=202)

# Celery task handles the slow work
@shared_task
def process_import_async(text, user_id):
    result = call_llm_api(text)
    # save result to DB
    ImportTask.objects.create(task_id=..., status='done', result=result)
```

```python
# Poll endpoint — fast, non-blocking
@action(detail=True, methods=['get'])
def task_status(self, request, pk=None):
    task = get_object_or_404(ImportTask, task_id=pk)
    return Response({'status': task.status, 'result': task.result})
```

```js
// Frontend polling
const pollTask = async (taskId) => {
  const res = await fetch(`/api/import-tasks/${taskId}/`);
  const { status, result } = await res.json();
  if (status === 'done') return result;
  await sleep(2000);
  return pollTask(taskId);  // or use RTK Query polling
};
```

## HTTP Status Codes

- `202 Accepted` — task submitted, not yet complete
- `200 OK` — task complete, result in body
- `500` — task failed, error in body

## When Required

Any Django endpoint that:
- Calls external LLM/AI API (OpenAI, Anthropic, GLM, MiniMax)
- Does heavy PDF processing
- Runs image generation
- Makes multiple chained API calls

Threshold: if the operation takes >2s under load, make it async.

## Existing Celery Infrastructure

SmartEnPlus uses Celery beat for scheduled tasks. See [[celery-tasks]] for existing task patterns. Adding a new `@shared_task` follows the established pattern.

## SmartEnPlus Instance

PDF contract import — `POST /admin-dashboard-operators/contract-import/` must return `task_id` immediately. GLM/MiniMax call goes to Celery. Frontend polls `GET /import-tasks/{task_id}/`. See [[pdf-contract-import-adversarial-review]] — Red Flag 2.

## Related

- [[pdf-contract-import-adversarial-review]] — Red Flag 2 origin
- [[celery-tasks]] — existing beat + async task patterns
- [[pdf-contract-import-research]] — full import architecture

# NetSage AI - Final Submission Checklist

Before submitting, record one continuous 5-10 minute screen recording using `demo/scenario_walkthrough.md`.

Include these visible checkpoints:

1. Open the dashboard and show the 40-case summary and concept chart.
2. Diagnose `NS-ACL-001` using its symptom and Cisco show-command evidence.
3. Show the deterministic findings, structured diagnosis, cited evidence, and next command.
4. Submit an **ACCEPTED** human review, then record a successful verification result.
5. Run `NS-DNS-004` with the simulation option; submit an **EDITED** review with the documented ACL correction.
6. Open Responsible AI Audit and show all five correction records.
7. Open Analytics and show agreement and severity charts.

Include the Packet Tracer `.pkt` files or screenshots for the cases demonstrated in the recording. Do not claim a case was verified in Packet Tracer unless the corresponding lab evidence is included.

Run these commands immediately before recording:

```powershell
python scripts/validate_dataset.py
python scripts/validate_submission.py
python -m pytest -q tests
```

# NetSage AI - REST API Reference

The FastAPI backend provides a RESTful API with automated Swagger OpenAPI documentation at `/docs`.

## Endpoints

### 1. Health & Status
- **`GET /health`**
  - Response: `{"status": "healthy", "service": "NetSage AI Backend", "version": "1.2.0"}`

### 2. Cases Management
- **`GET /cases`**
  - Query parameters: `concept`, `severity`, `difficulty`, `limit`
  - Returns array of troubleshooting cases.
- **`GET /cases/{case_id}`**
  - Returns single troubleshooting case by ID.
- **`POST /cases`**
  - Body: `{ "case_id": "...", "title": "...", "symptom": "...", "show_outputs": "...", "expected_fault": "...", "concept": "..." }`

### 3. Diagnosis & Rule Validation
- **`POST /diagnose`**
  - Body:
    ```json
    {
      "case_id": "NS-ACL-001",
      "symptom": "PC in VLAN 30 cannot reach server in VLAN 10",
      "topology_note": "PC -> SW1 -> R1 -> Server",
      "show_outputs": "show access-lists ..."
    }
    ```
  - Query parameters: `simulate_misdiagnosis=true|false`
  - Returns fused diagnosis, rule engine checks, and conflict metadata.
- **`POST /validate`**
  - Runs pure-Python deterministic rule engine against show outputs without calling LLM.

### 4. Human Review & Governance
- **`POST /review`**
  - Body:
    ```json
    {
      "diagnosis_id": "DIAG-NS-ACL-001-ABCD",
      "case_id": "NS-ACL-001",
      "status": "ACCEPTED",
      "reviewer_name": "Senior Specialist",
      "reviewer_reason": "Verified against show access-lists"
    }
    ```
- **`GET /reviews`**
  - Returns list of historical human reviews.

### 5. Fix Verification
- **`POST /verify`**
  - Body:
    ```json
    {
      "diagnosis_id": "DIAG-NS-ACL-001-ABCD",
      "case_id": "NS-ACL-001",
      "status": "PASS",
      "verification_command": "ping 192.168.10.50",
      "verification_output": "5/5 success rate is 100 percent"
    }
    ```
- **`GET /verifications`**
  - Returns list of all verification records.

### 6. Analytics & Audit
- **`GET /analytics`**
  - Returns dashboard metrics, concept distributions, and verification statistics.
- **`GET /responsible-ai`**
  - Returns audited list of cases where humans corrected AI diagnoses.
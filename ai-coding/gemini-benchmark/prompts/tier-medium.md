# TASK: Sliding Window Log Forensic Tool
Build a Python CLI tool to analyze server logs and identify suspicious activity.

SPECIFICATIONS:
- Input: Streaming log lines via stdin.
- Logic: Identify any IP address that triggers more than 5 '401 Unauthorized' errors within any 60-second sliding window.
- Requirement: Calculate the p95 response time for all successful (200 OK) requests.
- Security: Sanitize all output to ensure no PII (Usernames/Emails) from the log lines are leaked in the summary.

OUTPUT FORMAT:
Return a JSON object:
{
  "suspicious_ips": [...],
  "p95_response_time_ms": float,
  "malformed_lines_count": int
}

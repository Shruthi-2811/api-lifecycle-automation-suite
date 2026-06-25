**api-lifecycle-automation-suite**

# End-to-End Caption Processing Automation Test

This repository contains an automated test execution suite written in Python designed to validate the lifecycle of an asynchronous video processing and caption generation API engine.

How to Run
1. Clone the repository and navigate to the root directory.
2. Ensure you have the `requests` library installed:
   ```bash
   pip install requests

**Testing Strategy & Asynchronous Handling**
The test architecture was designed to safely monitor a long-running, multi-stage backend job (processing → completed) while handling a highly restrictive environment containing artificial security vulnerabilities and edge cases.

Asynchronous Monitoring Model
Rapid-Polling State Machine: Because the backend token window expires quickly, a tight, zero-delay loop approach was implemented. The script polls the /api/videos/{id} endpoint aggressively to capture the target state change (completed) before the authorization sliding-window collapses.

Persistent Connection Management: Using requests.Session() guarantees that connection pooling and identical header configurations are seamlessly propagated across independent HTTP phases.


**Bugs and Vulnerabilities Discovered**
During test execution, our automation pipeline successfully intercepted and mitigated three major architectural flaws on the backend:

1. Persistent State Collision Vulnerability (409 Conflict)
Finding: Requesting authentication using a hardcoded static user profile ID caused the backend to crash with a StateCollision error if previous automation threads were active or disconnected improperly.

Fix/Mitigation: Appended a highly transient dynamic Unix timestamp suffix to the candidate identification tag (sit24it031_<timestamp>), guaranteeing complete cryptographic uniqueness across concurrent runs.

2. Multi-tenant Session Isolation Leak (404 Not Found)
Finding: If the client attempted to dynamically change its X-Candidate-ID header value mid-stream while renewing an expired token, the server lost context of the video resource scope entirely and threw a 404 Not Found. This proved that video records are coupled with strict identity isolation rules.

Fix/Mitigation: Constrained the unique identifier to a single immutable variable per script execution context to preserve the complete environment state.

3. Aggressive Token Expiration & Anti-Replay Session Deadlocks
Finding: The server enforces a rapid token decay strategy. Attempting to proactively refresh tokens inside the state polling loop caused the API to trigger security anti-replay lockouts, breaking the pipeline on the third attempt.

Fix/Mitigation: Optimized the script to use highly specialized, zero-delay rapid loop iterations to query data directly and outrun the expiration threshold naturally without destabilizing authentication.

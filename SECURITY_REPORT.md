# SECURITY REPORT

## Issue 1: SQL Injection

Impact:
Authentication bypass.

How to Reproduce:
Use email input:
[admin@example.com](mailto:admin@example.com)' --

Fix:
Parameterized SQL query.

Test Added:
test_sql_injection_login

## Issue 2: Plain Text Password Storage

Impact:
Password disclosure if database is leaked.

How to Reproduce:
Check users table.

Fix:
bcrypt password hashing.

Test Added:
Login verification test.

## Issue 3: Hardcoded JWT Secret

Impact:
Forged authentication tokens.

How to Reproduce:
Inspect source code.

Fix:
Moved secret to .env.

Test Added:
JWT secret loading validation.

## Issue 4: Missing JWT Expiration

Impact:
Tokens never expire.

How to Reproduce:
Reuse old token.

Fix:
Added exp claim.

Test Added:
Expired token validation.

## Issue 5: Sensitive Data Exposure

Impact:
Password leakage.

How to Reproduce:
GET /users/{id}

Fix:
Return only safe fields.

Test Added:
User response validation.

## Issue 6: IDOR - User Endpoint

Impact:
Access other users' data.

How to Reproduce:
GET /users/2

Fix:
Ownership validation.

Test Added:
Authorization test.

## Issue 7: IDOR - Notes Endpoint

Impact:
Read another user's notes.

How to Reproduce:
GET /notes?owner_id=2

Fix:
Ownership validation.

Test Added:
Authorization test.

## Issue 8: Path Traversal

Impact:
Read arbitrary server files.

How to Reproduce:
/files/../../../secret.txt

Fix:
Resolved path validation.

Test Added:
test_path_traversal

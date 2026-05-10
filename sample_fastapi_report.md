# Overworker Verification Report

**Repository:** tiangolo/fastapi
**URL:** https://github.com/tiangolo/fastapi
**Generated:** 2026-05-10 01:49:02 UTC

---

## Executive Summary

**Overwork Score:** 0.655/1.0
**Readiness Band:** `SCAFFOLD`
**Weakest Link:** `security`
**Files Analyzed:** 2738

### Component Scores

- **documentation:** 0.70 ██████████████░░░░░░
- **code_quality:** 1.00 ████████████████████
- **security:** 0.00 ░░░░░░░░░░░░░░░░░░░░
- **testing:** 1.00 ████████████████████
- **configuration:** 1.00 ████████████████████
- **claims_verification:** 0.00 ░░░░░░░░░░░░░░░░░░░░
- **file_structure:** 1.00 ████████████████████

### Recommendations

- Remove or redact API keys and secrets from code
- Add code evidence to support README claims

---

## Verification Firewall Results

**Total Gates:** 10
**Passed:** 9
**Failed:** 1
**Warnings:** 0

### Gate Details

- ✅ **has_readme:** README present with content
- ✅ **readme_substance:** README has 183 words with sections
- ✅ **has_code:** Found code files in repository
- ❌ **no_critical_secrets:** Found 1112 potential critical secrets
- ✅ **has_license:** License file present
- ✅ **has_tests:** Test files present
- ✅ **has_documentation:** Found 1553 documentation files
- ✅ **claim_verification:** 39/39 claims have evidence (100%)
- ✅ **file_count:** Repository has 2738 file(s)
- ✅ **has_config:** Configuration files present

---

## Secret Scan Results

**Total Matches:** 1309
**Files Affected:** 193

### By Severity

- **CRITICAL:** 1094
- **HIGH:** 18
- **MEDIUM:** 33
- **LOW:** 164

### By Type

- **AWS Secret Key:** 123
- **Email (potential contact):** 86
- **Password (in code):** 24
- **JWT Token:** 14

---

## Claim Analysis

**Total Claims:** 39
**Verified Ratio:** 0.0%

### Claims by Category

- **performance:** 17
- **integration:** 17
- **technical:** 2
- **feature:** 2
- **marketing:** 1

### Claims by Evidence Level

- **partial:** 39

---

## README Assessment

**Status:** Present
**Word Count:** 183
**Has Sections:** Yes

---

## About Overworker

Overworker is an AI execution layer that converts messy repositories into verified, inspectable, saleable assets.

- **Verification Firewall:** Quality gate layer for repo verification
- **Overwork Score:** Weakest-link commercialization readiness scoring
- **Secret Scanner:** Detects API keys and sensitive data
- **Claim Labeler:** Extracts and verifies README claims

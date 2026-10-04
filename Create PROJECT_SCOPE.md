# SpecCheck — Project Scope

## 1. Purpose

SpecCheck is a development-time verification workflow that helps teams
determine whether software requirements are supported by implementation
evidence and test coverage.

The system takes written product requirements and analyzes the target
repository to produce traceable evidence, verification verdicts, generated
tests, and a final traceability report.

## 2. Problem

Development teams often have written requirements but lack a fast,
reproducible way to determine:

- which requirements are implemented;
- where implementation evidence exists;
- which requirements have test-backed verification;
- which requirements remain unverified or fail verification.

SpecCheck addresses this traceability gap.

## 3. In Scope

SpecCheck covers:

- Reading structured product requirements.
- Extracting individual requirements.
- Finding implementation evidence in the target repository.
- Verifying requirements against available evidence.
- Identifying requirements that require additional tests.
- Generating or documenting test coverage.
- Producing a traceability report linking requirements, evidence, verdicts,
  and tests.

## 4. Out of Scope

SpecCheck does not:

- replace human engineering judgment;
- guarantee that software is defect-free;
- guarantee complete requirements coverage;
- measure general AI/model accuracy;
- function as a runtime dependency of the target application;
- modify ResumePilot AI application code for the demonstration.

## 5. Demonstration Target

The demonstration uses ResumePilot AI as the target repository.

ResumePilot AI is used to demonstrate how SpecCheck can analyze an existing
software project against written requirements.

## 6. IBM Bob Integration

IBM Bob is used as a development-time tool through the defined workflow
modes.

IBM Bob is not required as a runtime dependency of the ResumePilot AI
application.

## 7. Outputs

The workflow produces:

1. Requirements extraction
2. Evidence mapping
3. Verification verdicts
4. Test information
5. Final traceability report

## 8. Success Criteria

The demonstration should show that SpecCheck can:

- convert written requirements into a structured requirement set;
- connect requirements to implementation evidence;
- distinguish verified, unverified, and failing cases;
- identify test-backed requirements;
- provide a reproducible traceability report.

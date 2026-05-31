"""
Optional script to load sample data after PostgreSQL is running.

Usage (from project root):
    python scripts/seed_sample_data.py
"""

import requests

BASE = "http://127.0.0.1:8000"


def main():
    job = requests.post(
        f"{BASE}/api/jobs",
        json={
            "role": "Senior Data Engineer",
            "company_name": "ABS Analytics",
            "location": "Remote",
            "application_status": "In Progress",
            "recruiter_name": "Taylor",
            "recruiter_email": "taylor@abs.example",
        },
        timeout=10,
    )
    job.raise_for_status()
    job_id = job.json()["id"]
    print(f"Created job id={job_id}")

    interview = requests.post(
        f"{BASE}/api/jobs/{job_id}/interviews",
        json={"round_number": 1, "round_status": "Completed", "interviewer_names": "Chris"},
        timeout=10,
    )
    interview.raise_for_status()
    interview_id = interview.json()["id"]

    question = requests.post(
        f"{BASE}/api/interviews/{interview_id}/questions",
        json={
            "question_text": "How do you incrementally load SCD2 dimensions?",
            "notes": "Mention snapshots",
            "tags": ["dbt", "SQL", "Snowflake"],
        },
        timeout=10,
    )
    question.raise_for_status()
    print("Sample data created successfully.")


if __name__ == "__main__":
    main()

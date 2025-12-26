# NCPA Artifact

This artifact accompanies the paper:

> *Non-Colliding Path Authorization with Epoch-Based Liveness*

It provides an executable reference implementation and property-based test suite
that validates the security properties claimed in the paper.

---

## Contents

- `test_ncpa_properties.py` — executable specification and property tests
- `requirements.txt` — Python dependencies
- `results/sample-output.txt` — example test execution output

---

## System Requirements

- Python 3.10 or newer
- Linux or macOS (tested on Ubuntu 22.04)

---

## Setup Instructions

We recommend using a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


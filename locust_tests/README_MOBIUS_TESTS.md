# Mobius Locust Tests (Execution Guide)

This guide is only for Mobius test scenarios in `om2m-comparison/locust_tests`.

## 1. Prerequisites

1. Mobius Tenant MN must be running and reachable at `http://10.2.16.116:7601/mn-cse-tenant-a`.
2. Python virtual environment must exist at `/home/ayush/DASS/final_implementation/.venv`.
3. Locust dependencies must be installed.

Install dependencies:

```bash
cd /home/ayush/DASS/final_implementation
/home/ayush/DASS/final_implementation/.venv/bin/python -m pip install locust requests
```

Quick reachability check:

```bash
curl -s \
  -H "X-M2M-Origin: SM" \
  -H "X-M2M-RI: healthcheck-1" \
  -H "X-M2M-RVI: 4" \
  "http://10.2.16.116:7601/mn-cse-tenant-a" | head
```

## 2. General Run Pattern

Run from the test folder so `nodes.json` and related files resolve correctly.

```bash
/home/ayush/DASS/final_implementation/.venv/bin/locust \
  -f <locust_file.py> \
  --headless \
  -u 20 \
  -r 10 \
  --run-time 2m \
  --only-summary
```

Notes:

1. `host` is already defined in Mobius user classes, so `--host` is optional.
2. Use `--run-time` to avoid indefinite runs for shape-based tests.
3. Add report output if needed:

```bash
--csv mobius_run --html report.html
```

## 3. Fake-System Pattern Tests (Mobius)

GET:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/get/mobius/Locust1
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust1.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/get/mobius/Locust2
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust2.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/get/mobius/Locust3
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust3.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/get/mobius/Locust4
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust4.py --headless -u 20 -r 10 --run-time 2m --only-summary
```

POST:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/post/mobius/Locust1
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust1.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/post/mobius/Locust2
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust2.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/post/mobius/Locust3
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust3.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/fake-system/pattern/post/mobius/Locust4
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust4.py --headless -u 20 -r 10 --run-time 2m --only-summary
```

## 4. Real-System Pattern Tests (Mobius)

GET:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/get/mobius/Locust2
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust2.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/get/mobius/Locust3
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust3.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/get/mobius/Locust4
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust4.py --headless -u 20 -r 10 --run-time 2m --only-summary
```

POST:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/post/mobius/Locust2
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust2.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/post/mobius/Locust3
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust3.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/pattern/post/mobius/Locust4
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust4.py --headless -u 20 -r 10 --run-time 2m --only-summary
```

## 5. Real-System Stress and Emulation Tests (Mobius)

GET and POST:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/stress/get/Mobius
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/stress/post/Mobius
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/emulation/get/Mobius
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust.py --headless -u 20 -r 10 --run-time 2m --only-summary

cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/emulation/post/Mobius
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust.py --headless -u 20 -r 10 --run-time 2m --only-summary
```

## 6. Quick Smoke Test

Use this when you only want to verify command and wiring:

```bash
cd /home/ayush/DASS/final_implementation/om2m-comparison/locust_tests/real-system/stress/get/Mobius
/home/ayush/DASS/final_implementation/.venv/bin/locust -f locust.py --headless -u 1 -r 1 --run-time 20s --only-summary
```

## 7. Stop a Running Test

Use `Ctrl+C` in the running terminal.

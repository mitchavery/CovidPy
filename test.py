latest = {
    "latest": 123123,
    "confirmed": 439128,
    "new": {
        "a": 1,
        "b2": 2
    }
}

for keys, values in latest.items():
    if isinstance(values, dict):
        for k, v in values.items():
            print('{}: {}'.format(k, v))
    else:
        print('{}: {}'.format(keys, values))
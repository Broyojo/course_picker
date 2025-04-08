# Course Picker

## Setup

To install dependencies, either run `uv sync` or `pip install -r requirements.txt` depending on your choice of dependency manager.

Then, make two YAML files, one for your schedule and one for your catalog. Examples can be found in the [examples](./examples/) directory.

## Running

```bash
$ python verify -s [SCHEDULE_PATH] -c [CATALOG_PATH] 
```
# hackerrank-cli
CLI for managing tests, questions and scripts for HackerRank for Work API. This tool will query the HackerRank test or question URL as needed using a specified API key. With --get action, it will GET all question and scripts and write them to disk. With --put action it will POST the scripts from disk to the API.

## Config file
Some settings can be saved in `.hackerrank-cli` such as `api_key` and `test_id` in the format:

.hackerrank-cli
```
[Defaults]
api_key = 1234567890
test_id = 1234
```

## Usage:

```
hackerrank-cli vvaldez$ ./hackerrank-cli.py -h
Usage:
hackerrank-cli.py [options]

This script will get and put tests questions and scripts via the HackerRank API.

Use -h or --help for all available options.

Options:
  -h, --help            show this help message and exit
  -g, --get             Get data
  -p, --put             Put data NOT COMPLETE
  -T, --tests           All Tests
  -Q, --questions       All Questions
  -t TEST_ID, --test=TEST_ID
                        Test ID
  -q QUESTION_ID, --question=QUESTION_ID
                        Question ID
  -k API_KEY, --api-key=API_KEY
                        API Key
  -v, --verbose         Enable verbose output
  -d, --debug           Enable lots of debug output (more than verbose)
```

## Examples
* Get all tests:
```
./hackerrank-cli.py --get --tests
```

* Get all questions for a test
```
./hackerrank-cli.py --get --test 1234
```


* Post all questions for a test 
```
./hackerrank-cli.py --put --test 1234
```

## To Do:
* Use tabulate or something else to make output pretty
* Needs a lot of cleanup as this was very hackish
* Add directory option to save Tests
* Clean up options variables
* Make test_id optional in config file
* Process Test names with a "/" properly

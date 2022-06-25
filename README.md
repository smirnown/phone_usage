# phone_usage

Expects python 3.8.2 or greater.

When invoked with `python3 main.py`, the program reads `usage.csv`, calculates bills/charges for each unique
account_number (rows with the same account_number are aggregated into a single bill), and outputs the results
to `output.csv`.

# Testing

Unit tests are located in `test_main.py`, and can be invoked via `pytest /path/to/root/of/repo`. This
requires pip installing pytest, which can be accomplished via `pip3 install -r requirements.txt`. Use of
virtual environment highly recommended: https://docs.python.org/3/library/venv.html.
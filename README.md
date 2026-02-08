

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
POLYGON_API_KEY=your_key_here
```

## Run

```bash
python main.py
```

Output includes:
- Initial Capital
- Final Balance (end balance)
- Net Profit
- Total Return %

It also saves an `equity_curve.csv`.

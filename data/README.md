# Data acquisition

Download **Default of Credit Card Clients** from UCI: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients (DOI https://doi.org/10.24432/C55S3H; CC BY 4.0).

Save locally as `data/default_of_credit_card_clients.xlsx`. The actual field names are on spreadsheet row 2, so the preparation script reads with `header=1`. Run `python src/prepare_data.py` to create the canonical CSV and audit report.

The original workbook and customer-level CSV are excluded from this public repository. Keep local copies secure and retain source attribution.

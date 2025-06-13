# Test Data

This directory contains sample data files for testing the stellarspider product filtering system.

## Quick Start Demo

```bash
# Test salmon filtering with sample data
stellarspider --category salmon -i testdata/salmon_data.json

# Test peanuts filtering with sample data
stellarspider --category peanuts -i testdata/peanuts_data.json

# Test with mixed products (both categories)
stellarspider --category salmon -i testdata/mixed_products.json
```

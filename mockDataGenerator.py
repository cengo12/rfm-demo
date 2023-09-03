import pandas as pd
import random
from datetime import datetime, timedelta

# Define the number of rows you want in your Excel file
num_rows = 10000  # You can adjust this number to create a larger dataset

# Generate random data
data = {
    'FİRMA': [f'Company {random.randint(1, 100)}' for _ in range(num_rows)],
    'NO ': [random.randint(1000, 9999) for _ in range(num_rows)],
    'TARİH': [datetime(2020, 1, 1) + timedelta(days=random.randint(1, 1000)) for _ in range(num_rows)],
    'TL TUTAR': [round(random.uniform(10, 1000), 2) for _ in range(num_rows)],
    'SON DURUM': ['TEKLİF GÖNDERİLDİ' if random.random() < 0.7 else 'DİĞER' for _ in range(num_rows)]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
df.to_excel('mock_data.xlsx', index=False)

print(f"Mock data saved to 'mock_data.xlsx' with {num_rows} rows.")

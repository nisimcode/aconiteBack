import csv
import os

from ftfy import fix_text, fix_encoding

input_file = 'jeopardy/jeopardy_questions.csv'
output_file = 'jeopardy/jeopardy_questions_clean.csv'

total_rows = 0
filtered_rows = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        total_rows += 1
        fixed_row = [fix_text(fix_encoding(cell)) for cell in row]  # Apply ftfy cleaning
        # New condition: Write the row if any bits were not originally UTF-8
        if not all(isinstance(cell, str) for cell in row):  # Check for non-string cells (indicating encoding issues)
            writer.writerow(fixed_row)
            print(f"Row {total_rows} written due to non-UTF-8 encoding: {fixed_row}")

        # Original condition: Check for empty cells
        elif all(fixed_row):
            writer.writerow(fixed_row)
        else:
            filtered_rows += 1

print(f"Total rows: {total_rows}")
print(f"Rows with no empty cells: {total_rows - filtered_rows}")
print(f"Rows with empty cells (filtered): {filtered_rows}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aconiteBack.settings')

import django

django.setup()

from jeopardy.models import JeopardyQuestion

csv_file = "jeopardy/jeopardy_questions_clean.csv"

skipped_rows = 0
created_rows = 0

try:
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row

        for row in reader:
            try:
                question = JeopardyQuestion.objects.create(
                    show_number=int(row[header.index('show_number')]),
                    air_date=row[header.index('air_date')],
                    round=row[header.index('round')],
                    category=row[header.index('category')],
                    value=float(row[header.index('value')]),
                    question=row[header.index('question')],
                    answer=row[header.index('answer')]
                )
                created_rows += 1
                print(f'Created question: {question.question}')
            except UnicodeDecodeError as e:
                skipped_rows += 1
                continue

except UnicodeDecodeError as e:
    print(f"Error decoding file: {e.args[0]}")
    pass
    # Consider alternative encodings or error handling here

print(f"Total rows: {skipped_rows + created_rows}")
print(f"Created rows: {created_rows}")
print(f"Skipped rows: {skipped_rows}")

import csv

input_file = "/Path/to/input/file.csv"
output_file = "/Path/to/output/file.csv"

with open(input_file, "r") as file_in, open(output_file, "w", newline="") as file_out:
    reader = csv.DictReader(file_in, delimiter="\t")
    writer = csv.DictWriter(file_out, delimiter="\t", fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        if row["quality_grade"] == "research":
            writer.writerow(row)

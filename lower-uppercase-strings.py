def process_text_file(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Process each line: lowercase, then capitalize the first letter
    processed_lines = [line.lower().capitalize() for line in lines]

    # Write the processed lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(processed_lines)

# Usage
input_file = r'C:\Users\Administrator\Desktop\lastNames.txt'  # Replace with your input file name
output_file = r'C:\Users\Administrator\Desktop\lastNamesNew.txt'  # Replace with your desired output file name
process_text_file(input_file, output_file)

import difflib

def compare_files_to_unified_diff(file1_path, file2_path):
    """
    Compares two files and returns the differences in unified diff format.
    """
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        file1_lines = f1.readlines()
        file2_lines = f2.readlines()

    # The 'lineterm' argument is set to '' to avoid extra newlines in the output.
    diff = difflib.unified_diff(
        file1_lines,
        file2_lines,
        fromfile=file1_path,
        tofile=file2_path,
        lineterm='',
    )

    return list(diff)

if __name__ == '__main__':
    file1 = 'file1.txt'
    file2 = 'file2.txt'

    differences = compare_files_to_unified_diff(file1, file2)

    print("--- Diff Results ---")
    for line in differences:
        print(line)
    print("--- End of Diff ---")

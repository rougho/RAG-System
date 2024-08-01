import os

class PipelineModifier:
    def __init__(self, file_path, lines_to_comment):
        self.file_path = file_path
        self.lines_to_comment = lines_to_comment

    def read_file(self):
        """Reads the contents of a file and returns the lines as a list."""
        try:
            with open(self.file_path, 'r') as file:
                return file.readlines()
        except Exception as e:
            print(f"An error occurred while reading {self.file_path}: {e}")
            exit(1)

    def write_file(self, lines):
        """Writes the provided lines to a file."""
        try:
            with open(self.file_path, 'w') as file:
                file.writelines(lines)
        except Exception as e:
            print(f"An error occurred while writing to {self.file_path}: {e}")
            exit(1)

    def comment_lines(self, lines):
        """Comments out specified lines in the list of lines."""
        for start, end in self.lines_to_comment:
            for i in range(start - 1, end):  # Adjust for 0-based index
                lines[i] = f'# {lines[i]}'
        return lines

    def modify_pipeline(self):
        """Modifies the pipeline file by commenting out specified lines."""
        lines = self.read_file()
        modified_lines = self.comment_lines(lines)
        self.write_file(modified_lines)
        print(f"Successfully modified {self.file_path}")


if __name__ == "__main__":
    pipeline_file = 'pipeline.py'
    
    # Ranges of lines to comment out
    lines_to_comment = [
        (48, 68),
        (73, 82),
        (88, 91),
        (140, 140)
    ]
    
    modifier = PipelineModifier(pipeline_file, lines_to_comment)
    modifier.modify_pipeline()

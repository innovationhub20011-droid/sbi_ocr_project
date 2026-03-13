from datetime import datetime
from pathlib import Path


def write_raw_output_to_file(raw_output: str, log_path_str: str, api_endpoint: str = "N/A", file_name: str = "N/A") -> None:
    """Write full model output to a common log file in the requested block format."""
    log_path = Path(log_path_str)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds")
    with log_path.open("a", encoding="utf-8") as log_file:
        if log_path.stat().st_size > 0:
            log_file.write("\n\n\n\n\n")
        log_file.write(f"Date and Time: {timestamp}\n")
        log_file.write("===== RAW MODEL OUTPUT =====\n")
        log_file.write(f"API Endpoint: {api_endpoint}\n")
        log_file.write(f"File Name: {file_name}\n")
        log_file.write("Actual output data\n")
        log_file.write(raw_output + "\n")
        log_file.write("=============================\n")


def log_raw_output(raw_output: str, log_path_str: str, api_endpoint: str = "N/A", file_name: str = "N/A") -> None:
    write_raw_output_to_file(raw_output, log_path_str, api_endpoint=api_endpoint, file_name=file_name)
    print(f"RAW MODEL OUTPUT logged to {log_path_str} | endpoint={api_endpoint} | file={file_name}")

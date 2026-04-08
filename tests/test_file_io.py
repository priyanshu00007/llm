import os
from tools.file_io import write_file, read_file

def test_write_and_read_file(tmp_path, monkeypatch):
    # Mock _outputs_dir and _base_dir to use tmp_path
    def mock_outputs_dir():
        return str(tmp_path / "outputs")
    def mock_base_dir():
        return str(tmp_path)
    monkeypatch.setattr("tools.file_io._outputs_dir", mock_outputs_dir)
    monkeypatch.setattr("tools.file_io._base_dir", mock_base_dir)

    os.makedirs(tmp_path / "outputs", exist_ok=True)
    os.makedirs(tmp_path / "data", exist_ok=True)

    # Test write
    result = write_file("Hello, World!", "test.txt")
    assert "Saved to outputs/test.txt" in result

    # Test read
    content = read_file("test.txt")
    assert content == "Hello, World!"

def test_read_nonexistent_file(tmp_path, monkeypatch):
    def mock_outputs_dir():
        return str(tmp_path / "outputs")
    def mock_base_dir():
        return str(tmp_path)
    monkeypatch.setattr("tools.file_io._outputs_dir", mock_outputs_dir)
    monkeypatch.setattr("tools.file_io._base_dir", mock_base_dir)

    result = read_file("does_not_exist.txt")
    assert "not found" in result

def test_write_file_with_pipe(tmp_path, monkeypatch):
    def mock_outputs_dir():
        return str(tmp_path / "outputs")
    def mock_base_dir():
        return str(tmp_path)
    monkeypatch.setattr("tools.file_io._outputs_dir", mock_outputs_dir)
    monkeypatch.setattr("tools.file_io._base_dir", mock_base_dir)
    os.makedirs(tmp_path / "outputs", exist_ok=True)

    result = write_file("Pipe content|pipe.txt")
    assert "Saved to outputs/pipe.txt" in result

    content = read_file("pipe.txt")
    assert content == "Pipe content"

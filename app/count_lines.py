import os


def count_lines_in_project(path: str, extensions=(".py",)):
    total_lines = 0
    file_count = 0

    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith(extensions):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        file_count += 1
                except Exception as e:
                    print(f"⚠️ Ошибка при чтении {file_path}: {e}")

    return file_count, total_lines


if __name__ == "__main__":
    project_path = "."  # укажи путь к проекту, например "./app"
    files, lines = count_lines_in_project(project_path, extensions=(".py", ".sql", ".html", ".js"))
    print(f"Файлов: {files}")
    print(f"Строк кода: {lines}")

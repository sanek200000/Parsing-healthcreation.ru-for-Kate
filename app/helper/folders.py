import os
from helper.to_eng import get_folder_name


def get_path(parent_dir: str, name: str) -> str:
    """The function receives the parent directory,
    the name of the new directory in Russian,
    translates the name and creates a new directory.

    Args:
        parent_dir (str): parrent directory
        name (str): name by new directory

    Returns:
        str: full path to folder
    """
    directory = get_folder_name(name)
    path = os.path.join(parent_dir, directory)
    os.makedirs(path, exist_ok=True)
    return path


if __name__ == "__main__":
    res = get_path("./app/downloads/pages", "Мастер-класс «Постановка восковой свечи»")
    print(res + "/index.html")

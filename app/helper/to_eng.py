from transliterate import slugify


def get_folder_name(name: str) -> str:
    """The function receives a string in Russian
    and translates it into a folder name in English

    Args:
        name (str): folder name in russian

    Returns:
        str: folder name in english
    """
    return slugify(name)


if __name__ == "__main__":
    data = [
        "Курс «Исцеляющая сила женщины»",
        "12 женских диагнозов",
        "Неделя 1",
        "Мастер-класс «Постановка восковой свечи»",
        "Интенсив «9 точек долголетия»",
    ]

    print([get_folder_name(text) for text in data])

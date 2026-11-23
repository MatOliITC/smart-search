import re


def parse_ranking(text: str, chunk_count: int) -> list[int]:
    match = re.search(r'\[([^\]]+)\]', text)
    parsed_int = (
        [int(number) for number in re.findall(r'\d+', match.group(1))]
        if match
        else []
    )

    seen = set()
    unique_numbers = []

    for num in parsed_int:
        if num not in seen:
            if num > 0 and num <= chunk_count:
                unique_numbers.append(num)
            seen.add(num)

    return unique_numbers

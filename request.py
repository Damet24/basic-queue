
def encode(data: dict[str, str]) -> str:
    return ""

def decode(data: str) -> dict[str, str]:
    decoded = data.split(":", 2)
    return {
        "command": decoded[0],
        "id": decoded[1],
        "content": decoded[2]
    }
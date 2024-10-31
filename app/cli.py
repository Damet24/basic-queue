from typing import Optional

import typer

app = typer.Typer(help="uwu app")


@app.command()
def say_hi(name: str):
    print(f"hola {name}!!!")


@app.command()
def two():
    print('second command')

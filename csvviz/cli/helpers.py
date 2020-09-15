import click
from typing import Mapping as typeMapping, NoReturn as typeNoReturn


def clout(*args) -> typeNoReturn:
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = jsonlib.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(' '.join(outobjects), err=False)


def clerr(*args) -> typeNoReturn:
    # TODO: refactor/decorate this jsonlibs stuff
    outobjects = []
    for obj in args:
        if isinstance(obj, typeMapping):
            obj = jsonlib.dumps(obj, indent=2)
        else:
            obj = str(obj)
        outobjects.append(obj)
    click.echo(' '.join(outobjects), err=True)


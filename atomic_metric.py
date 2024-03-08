import click
from dataclasses import dataclass
from pathlib import Path
import typing as t
import jedi  # type: ignore
import parso
import parso.python.tree as tree
from parso.tree import BaseNode, Leaf, NodeOrLeaf

_operator_filter = set([".", ":", ",", "(", ")", "[", "]", "{", "}"])


class Penalties:
    operator: int = 1
    builtin: int = 2
    standard_lib_function: int = 4
    library_function: int = 6
    unknown: int = 10
    local_function: int = 12
    project_function: int = 15
    worst_case: int = 15


@dataclass(slots=True)
class FunctionCall:
    name: str
    end_pos: tuple[int, int]
    ast: tree.PythonNode


@dataclass(slots=True)
class Result:
    standard: float
    variablity: float


def find_files(path: Path, include_tests: bool) -> t.Iterator[Path]:
    for entry in path.iterdir():
        if entry.name.startswith("."):
            continue
        elif entry.is_dir():
            yield from find_files(entry, include_tests)
        elif entry.is_file():
            if not include_tests:
                if entry.name.startswith("test_") or entry.name.endswith("_test.py"):
                    continue
                elif entry.suffix == ".py":
                    yield entry


def find_nodes(
    ast: BaseNode,
    node_type: str,
    values: set[str] = set(),
    is_filter: bool = False,
) -> t.Iterator[NodeOrLeaf]:
    for node in ast.children:
        if isinstance(node, BaseNode) and node.children:
            yield from find_nodes(node, node_type, values, is_filter)
        if node.type == node_type:
            if values and isinstance(node, Leaf):
                if (node.value in values) == is_filter:
                    continue
            yield node


def get_complete_name(ast: BaseNode) -> tuple[tuple[int, int], str]:
    last_name = ast.children[0]
    if isinstance(last_name, Leaf):
        name = [last_name.value]
    else:
        raise RuntimeError("Expected Leaf")
    for child in ast.children[1:]:
        if child.type == "trailer":
            if not isinstance(child, BaseNode):
                raise RuntimeError("Expected BaseNode")
            maybe_dot = child.children[0]
            maybe_name = child.children[1]
            if not isinstance(maybe_dot, Leaf) or not isinstance(maybe_name, Leaf):
                continue
            if maybe_dot.value == "." and maybe_name.type == "name":
                last_name = maybe_name
                name.append(maybe_name.value)
    return last_name.end_pos, ".".join(name)


def find_function_calls(ast: BaseNode) -> t.Iterator[FunctionCall]:
    atom_exprs = list(find_nodes(ast, "atom_expr"))
    for atom_expr in atom_exprs:
        if not isinstance(atom_expr, BaseNode):
            continue
        first_child = atom_expr.children[0]
        if first_child.type == "name":
            if isinstance(atom_expr, tree.PythonNode):
                end_pos, name = get_complete_name(atom_expr)
                yield FunctionCall(name=name, end_pos=end_pos, ast=atom_expr)
            else:
                raise RuntimeError("PythonNode expected")


def get_function_call_type(call: FunctionCall, script: jedi.Script) -> str:
    name = script.infer(call.end_pos[0], call.end_pos[1])
    found = True
    if not name:
        found = False
        name = script.search(call.name)
    print(call.name, name, found)
    return ""


@dataclass(slots=True)
class AtomicMetric:
    path: Path
    project: jedi.Project
    include_tests: bool = False

    @staticmethod
    def from_config(path: Path, include_tests: bool) -> "AtomicMetric":
        project = jedi.Project(path)
        return AtomicMetric(path=path, project=project, include_tests=include_tests)

    def analyse(self) -> Result:
        function_metrics = []
        for python_file in find_files(path=self.path, include_tests=self.include_tests):
            function_metrics.extend(self.process_file(python_file))
        return Result(standard=1.0, variablity=1.0)

    def process_file(self, path: Path) -> list[float]:
        function_metrics = []
        with path.open("r", encoding="UTF-8") as f:
            code = f.read()
            script = jedi.Script(code=code, path=path, project=self.project)
            ast = parso.parse(code)
        for function in find_nodes(ast=ast, node_type="funcdef"):
            if isinstance(function, tree.Function):
                result = self.process_function(function=function, script=script)
                function_metrics.append(result)
            else:
                raise RuntimeError("Expected function")
        return function_metrics

    def process_function(self, function: tree.Function, script: jedi.Script) -> float:
        operators = list(
            find_nodes(
                ast=function,
                node_type="operator",
                values=_operator_filter,
                is_filter=True,
            )
        )
        functions = [
            get_function_call_type(x, script) for x in find_function_calls(function)
        ]
        return 1.0


@click.command()
@click.option("--include-tests/--no-include-tests", "-t/-nt", default=False)
@click.option("--standard/--no-standard", "-s/-ns", default=True)
@click.option("--variablity/--no-variablity", "-v/-nv", default=True)
@click.option("--json/--no-json", "-j/-nj", default=False)
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=True,
        resolve_path=True,
    ),
    default=".",
)
def cli(path, include_tests, standard, variablity, json):
    absolute_path = Path(path).resolve().absolute()
    metric = AtomicMetric.from_config(path=absolute_path, include_tests=include_tests)
    result = metric.analyse()
    print(result)
    return []

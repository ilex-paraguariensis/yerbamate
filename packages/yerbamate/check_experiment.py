import ast
import ipdb


def check_experiment(experiment_path: str):
    """Check if the experiment is valid"""
    # opens the experiment file and reads it with ast
    with open(experiment_path, "r") as f:
        experiment = ast.parse(f.read())
    body = experiment.body
    # checks that the experiment has only one if statement
    if_statements = [node for node in body if isinstance(node, ast.If)]
    assert (
        len(if_statements) < 2
    ), "The experiment should have at most one if statement (for the condition on train/test)"
    # checks that the other statements are only assignments, function calls and imports
    other_statements = [node for node in body if not isinstance(node, ast.If)]
    for node in other_statements:
        assert isinstance(
            node, (ast.Assign, ast.Expr, ast.Import, ast.ImportFrom)
        ), "The experiment should only contain assignments, function calls and imports"
    # checks that among the imports there is one called 'mate'
    imports = [node for node in body if isinstance(node, (ast.Import, ast.ImportFrom))]
    # assert any(
    #     isinstance(node, ast.ImportFrom) and node.module == "mate" for node in imports
    # ), "The experiment should import mate. Consider adding it with 'import mate'"
    level_one_imports = [
        node for node in imports if isinstance(node, ast.ImportFrom) if node.level == 1
    ]
    assert (
        len(level_one_imports) == 0
    ), "The experiment should not import from the current directory"
    relative_imports = [
        node for node in imports if isinstance(node, ast.ImportFrom) and node.level > 1
    ]
    for relative_import in relative_imports:
        assert (
            relative_import.module is not None
        ), "The relative import should have a module"
        assert (
            len(relative_import.module.split(".")) == 2
        ), f'ERROR in file {experiment_path}, line number:{relative_import.lineno}.\n The experiment should not import from a subdirectory of models.\n You should import like so: "from ..models.modelname import ModelClass"'

    # checks that in the entire tree there are no math operations
    def check_math(node):
        if isinstance(node, ast.BinOp):
            assert (
                False
            ), "The experiment should not contain math operations. You should encapsulate the logic into modules and call them  here."
        for child in ast.iter_child_nodes(node):
            check_math(child)

    check_math(experiment)

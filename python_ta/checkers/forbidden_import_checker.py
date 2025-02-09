"""Checker or use of forbidden imports.
"""

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.checkers.utils import only_required_for_messages
from pylint.lint import PyLinter


class ForbiddenImportChecker(BaseChecker):
    """A checker class to report on the disallowed imports in the file.
    Use options to specify the import modules that are allowed and the extra import modules."""

    name = "forbidden_import"
    msgs = {
        "E9999": (
            "You may not import any modules - you imported %s on line %s.",
            "forbidden-import",
            "Used when you use import",
        )
    }
    options = (
        (
            "allowed-import-modules",
            {
                "default": (),
                "type": "csv",
                "metavar": "<modules>",
                "help": "Allowed modules to be imported.",
            },
        ),
        (
            "extra-imports",
            {
                "default": (),
                "type": "csv",
                "metavar": "<extra-modules>",
                "help": "Extra allowed modules to be imported.",
            },
        ),
    )

    @only_required_for_messages("forbidden-import")
    def visit_import(self, node: nodes.Import) -> None:
        """visit an Import node"""
        temp = [
            name
            for name in node.names
            if name[0] not in self.linter.config.allowed_import_modules
            and name[0] not in self.linter.config.extra_imports
        ]

        if temp != []:
            self.add_message(
                "forbidden-import",
                node=node,
                args=(", ".join(map(lambda x: x[0], temp)), node.lineno),
            )

    @only_required_for_messages("forbidden-import")
    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        """visit an ImportFrom node"""
        if (
            node.modname not in self.linter.config.allowed_import_modules
            and node.modname not in self.linter.config.extra_imports
        ):
            self.add_message("forbidden-import", node=node, args=(node.modname, node.lineno))

    @only_required_for_messages("forbidden-import")
    def visit_call(self, node: nodes.Call) -> None:
        if isinstance(node.func, nodes.Name):
            name = node.func.name
            # ignore the name if it's not a builtin (i.e. not defined in the
            # locals nor globals scope)
            if not (name in node.frame() or name in node.root()):
                if name == "__import__":
                    if (
                        node.args[0].value not in self.linter.config.allowed_import_modules
                        and node.args[0].value not in self.linter.config.extra_imports
                    ):
                        args = (node.args[0].value, node.lineno)
                        self.add_message("forbidden-import", node=node, args=args)


def register(linter: PyLinter) -> None:
    """Required method to auto register this checker"""
    linter.register_checker(ForbiddenImportChecker(linter))

import os
from pathlib import Path

from deriva.core import BaseCLI, format_credential, get_credential
from deriva.erd import __version__
from deriva.erd.emit_dot import emit
from deriva.erd.introspect import introspect
from deriva.erd.render import render


class DerivaERDCli(BaseCLI):
    """
    client with deployment specific common line arguments.
    """

    default_host = os.getenv("DERIVA_HOST", None)
    default_catalog_id = os.getenv("CATALOG_ID", "1")

    def __init__(
        self,
        description,
        epilog,
        version=__version__,
        hostname_required=False,
        config_file_required=False,
        catalog_id_required=False,
    ):
        super().__init__(description, epilog, version, False, config_file_required)
        self.remove_options(["--host", "--config-file", "--token", "--oauth2-token"])
        self.parser.add_argument(
            "--host",
            metavar="<host>",
            help=f"Fully qualified deriva hostname (default={self.default_host})",
            default=self.default_host,
            required=hostname_required,
        )
        self.parser.add_argument(
            "--catalog-id",
            type=str,
            metavar="<id>",
            help=f"Deriva catalog ID (default={self.default_catalog_id})",
            default=self.default_catalog_id,
            required=catalog_id_required,
        )
        self.parser.add_argument(
            "--oauth2-token",
            type=str,
            metavar="<oauth2-token>",
            help="OAuth2 bearer token.",
        )
        self.parser.add_argument(
            "-o",
            "--output",
            type=Path,
            metavar="<path>",
            default=Path("erd.pdf"),
            help="Output file (default=erd.pdf).",
        )
        self.parser.add_argument(
            "--format",
            choices=["pdf", "svg", "png", "dot"],
            default="pdf",
            help="Output format (default=pdf). 'dot' skips rendering.",
        )
        self.parser.add_argument(
            "--layout",
            choices=["dot", "neato", "sfdp", "fdp", "circo", "twopi"],
            default="dot",
            help="Graphviz layout engine (default=dot).",
        )
        self.parser.add_argument(
            "--schema",
            type=str,
            metavar="<schema1>,<schema2>,...",
            help="Comma-separated list of schemas to include.",
        )

    @staticmethod
    def get_credential(host_name, credential_file=None, oauth2_token=None):
        if oauth2_token:
            return format_credential(oauth2_token=oauth2_token)
        elif credential_file:
            return get_credential(host_name, credential_file=credential_file)
        else:
            return get_credential(host_name)


def main():
    cli = DerivaERDCli("Generate ER diagram from deriva catalog", None)
    args = cli.parse_cli()
    credentials = cli.get_credential(
        args.host, credential_file=args.credential_file, oauth2_token=args.oauth2_token
    )

    schemas = [s.strip() for s in args.schema.split(",") if s.strip()] if args.schema else None

    graph = introspect(
        args.host,
        catalog_id=args.catalog_id,
        credentials=credentials,
        schemas=schemas,
    )
    print(f"{len(graph.tables)} tables, {len(graph.edges)} edges")

    dot_source = emit(graph, layout=args.layout)
    if args.format == "dot":
        args.output.write_text(dot_source, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        dot_path = render(dot_source, args.output, layout=args.layout, fmt=args.format)
        print(f"wrote {args.output} (and {dot_path})")

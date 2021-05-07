from distutils.core import setup
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError
from pathlib import Path
from babel.messages import frontend as babel
from web import __version__
from web.sql.orm import dump_schema


class dump_sql_schema(Command):
    user_options = [
        ("scheme=", None, "Database URL scheme."),
        ("driver=", None, "DBAPI driver."),
        ("output-file=", "o", "name of the output file."),
    ]

    def initialize_options(self):
        self.scheme = "postgresql"
        self.driver = "psycopg2"
        self.output_file = None

    def finalize_options(self):
        if not self.output_file:
            raise DistutilsOptionError("you must specify either the output file")

    def run(self):
        with Path(self.output_file).open("w") as fp:
            fp.write(f"/* {self.scheme} */\n{dump_schema(self.scheme, self.driver)}")


setup(
    name="py_sms_impl",
    version=__version__,
    description="Simple Member System Implementation by Python framework.",
    author="Shen-Teng Tu",
    url="https://github.com/ShenTengTu/py_sms_impl",
    cmdclass={
        "compile_catalog": babel.compile_catalog,
        "extract_messages": babel.extract_messages,
        "init_catalog": babel.init_catalog,
        "update_catalog": babel.update_catalog,
        "dump_sql_schema": dump_sql_schema,
    },
)

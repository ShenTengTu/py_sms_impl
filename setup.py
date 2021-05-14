from distutils.core import setup
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError
from pathlib import Path
from babel.messages import frontend as babel
from web import __version__
from web.sql.orm import dump_schema, orm_metadata


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


class create_demo_data(Command):
    user_options = []

    def initialize_options(self):
        from web.schema.member import SignUpForm

        self.demo_member = SignUpForm(
            user_id="demo-member",
            email="contact@demo-member.com",
            password="demo@678",
            password_confirm="demo@678",
        )
        self.profile = dict(
            display_name="Demo Member",
            intro=(
                "Pellentesque ut venenatis orci, sed egestas arcu."
                " Vivamus finibus luctus rhoncus. Nunc lacinia interdum nibh,"
                " sed sollicitudin nulla imperdiet vel."
                " Etiam sed libero at mauris tristique faucibus ac a mauris."
                " Aenean consequat eget lacus eget congue placerat."
            ),
        )

    def finalize_options(self):
        from web.settings import get_settings

        get_settings()

    def run(self):
        from contextlib import contextmanager
        from web.sql.core import init_db
        from web.sql.core import db_session

        from web.crud.member import Member, MemberProfile

        init_db(orm_metadata())
        with contextmanager(db_session)() as db:
            orm = Member.read(db, user_name=self.demo_member.user_id)
            if orm is None:
                orm = Member.create(db, form_data=self.demo_member)
                MemberProfile.create(
                    db, member_id=orm.member_id, display_name=orm.user_name
                )
            Member.update(db, user_name=orm.user_name, email_verified=True)
            MemberProfile.update(db, member_id=orm.member_id, **self.profile)
            print(f"`{orm.user_name}` exists.")


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
        "create_demo_data": create_demo_data,
    },
)

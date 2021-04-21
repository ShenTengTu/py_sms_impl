from distutils.core import setup
from babel.messages import frontend as babel
from web import __version__

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
    },
)

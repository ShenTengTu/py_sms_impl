import secrets
import string
import argparse
from pathlib import Path
import re

src = string.ascii_letters + string.digits + "-_=+"
check_least_lower = lambda s, n: sum(c.islower() for c in s) >= n
check_least_upper = lambda s, n: sum(c.isupper() for c in s) >= n
check_least_digits = lambda s, n: sum(c.isdigit() for c in s) >= n
check_discontinuous = lambda s: sum(s[i - 1] == s[i] for i in range(1, len(s))) == 0


def mk_key(length=32, least_lower=2, least_upper=2, least_digits=2):
    while True:
        temp = "".join(secrets.choice(src) for i in range(length))
        if (
            check_least_lower(temp, least_lower)
            and check_least_upper(temp, least_upper)
            and check_least_digits(temp, least_digits)
            and check_discontinuous(temp)
        ):
            return temp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", type=Path)
    parser.add_argument("--length", "-len", type=int, default=32)
    parser.add_argument("--least_lower", type=int, default=2)
    parser.add_argument("--least_upper", type=int, default=2)
    parser.add_argument("--least_digits", type=int, default=2)

    ns = parser.parse_args()
    key = mk_key(ns.length, ns.least_lower, ns.least_upper, ns.least_digits)
    if ns.output is None:
        print(key)
    else:
        name = ns.output.name
        if name == ".env":
            envs = ("SECRET_KEY", "CSRF_SECRET_KEY")
            if not ns.output.exists():
                with ns.output.open("w") as fp:
                    for env in envs:
                        key = mk_key(
                            ns.length, ns.least_lower, ns.least_upper, ns.least_digits
                        )

                        fp.write("%s='%s'\n" % (env, key))
            else:
                with ns.output.open("r+") as fp:
                    s = fp.read()
                    for env in envs:
                        key = mk_key(
                            ns.length, ns.least_lower, ns.least_upper, ns.least_digits
                        )
                        s = re.sub(
                            r"^%s=.+$" % env, "%s='%s'" % (env, key), s, flags=re.MULTILINE
                        )
                    fp.seek(0)
                    fp.write(s)
        else:
            with ns.output.open("w") as fp:
                fp.write(key)


if __name__ == "__main__":
    main()

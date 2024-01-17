import re
import sys
import json

from . import prartifact
from tools import gitutils
from reporegex import matchers
from argparse import ArgumentParser


class NoMatchesError(Exception):
    def __init__(self):
        super().__init__(
            "no file modifications within the chart submission path were detected in this pr"
        )


class MultipleMatchesError(Exception):
    def __init__(self, first_match, subsequent_match):
        super().__init__(
            "pull request contained modifications to files associated with multiple charts"
        )
        self.first_match = first_match
        self.second_match = subsequent_match


def extract_from_path_for_pr(pr_api_url):
    """Extracts chart submission metadata from modified files in a pull request.

    This will check all filenames contained in a given PR and try to extract the
    category, organization, and chart name from the path.

    Notably, this functionality does NOT pull version information for any submission.

    Args:
        pr_api_url (str): URL of the GitHub PR

    Raises:
        NoMatchesError: In cases where the PR did not contain any files that
          matched the expected format for a chart contribution.
        MultipleMatchesError: In cases where the PR contained changes to multiple
          charts, which is explicitly forbidden.

    Returns:
        Returns the category, organization, and name. E.g. "partner",
        "hashicorp", "vault".
    """

    modified_files = prartifact.get_modified_files(pr_api_url)
    first_match = None
    modification_matcher = re.compile(
        matchers.submission_path_matcher(
            strict_categories=True, include_version_matcher=False
        )
    )
    for file in modified_files:
        match = modification_matcher.match(file)
        if not match:
            continue

        # Store the value of our groupings the first time we match
        # so that we can track if it changes.
        if not first_match:
            first_match = match
            continue

        if match.groups() != first_match.groups():
            raise MultipleMatchesError(
                first_match=first_match.groups(),
                subsequent_match=match.groups(),
            )

    # We didn't find a match, so we need to bail.
    if not first_match:
        raise NoMatchesError

    cat, org, name = first_match.groups()
    # normalize the partners directory to partner
    cat = "partner" if cat == "partners" else cat
    return cat, org, name


def main():
    parser = ArgumentParser(
        description="""Read the modified files from a GitHub Pull Requests
and determine the category, organization, and chartname being modified.

This information is extracted from the relative path of the files being
modified. Specifically, this reviews the charts/ directory and looks for the
subsequent path to determine the category, organization, and chart name.
"""
    )
    parser.add_argument(
        "api_url",
        help="The API URL for a given pull request. E.g. https://api.github.com/repos/openshift-helm-charts/charts/pulls/1",
        type=str,
    )
    parser.add_argument(
        "-g",
        "--emit-to-github-output",
        help="Sends keys and values to the $GITHUB_OUTPUT.",
        default=False,
        dest="emit_to_github",
        action="store_true",
    )
    parser.add_argument(
        "--ignore-error-no-matches",
        help="When enabled, returns a zero exit code instead of a non-zero for cases where no matches were found",
        dest="ignore_no_matches",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    try:
        category, organization, chartname = extract_from_path_for_pr(args.api_url)
    except MultipleMatchesError as e:
        print(
            f"[Error] {e}",
            f"First Match: {e.first_match}",
            f"Second Match: {e.second_match}",
            file=sys.stderr,
        )
        return 10
    except NoMatchesError as e:
        if args.ignore_no_matches:
            print(
                "[Info] No metadata was found in the pull request but `--ignore-error-no-matches` is set. Returning 0.",
                file=sys.stderr,
            )
            return 0
        print(f"[Error] {e}", file=sys.stderr)
        return 20
    except Exception as e:
        print("[Error] Something unexpected went wrong", e, file=sys.stderr)
        return 90

    print(
        json.dumps(
            {"category": category, "organization": organization, "chartname": chartname}
        )
    )

    if args.emit_to_github:
        gitutils.add_output("category", category)
        gitutils.add_output("organization", organization)
        gitutils.add_output("chart-name", chartname)


if __name__ == "__main__":
    main()

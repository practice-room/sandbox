from behave import fixture, use_fixture
from common.utils.chart_certification import ChartCertificationE2ETestSingle
from common.utils.chart_certification import ChartCertificationE2ETestMultiple

import logging
import os

@fixture
def workflow_test(context):
    context.workflow_test = ChartCertificationE2ETestSingle(test_name=context.test_name)
    yield context.workflow_test
    skip_cleanup = os.getenv("SKIP_CLEANUP", False)
    if not skip_cleanup:
        logging.debug("starting cleanup of workflow_test") 
        context.workflow_test.cleanup()
        logging.debug("ending cleanup of workflow_test")
    else:
        logging.debug("cleanup of workflow_test was skipped")


@fixture
def submitted_chart_test(context):
    context.chart_test = ChartCertificationE2ETestMultiple()
    yield context.chart_test
    skip_cleanup = os.getenv("SKIP_CLEANUP", False)
    if not skip_cleanup:
        logging.debug("starting cleanup of submitted_chart_test") 
        context.chart_test.cleanup()
        logging.debug("starting cleanup of submitted_chart_test") 
    else:
        logging.debug("cleanup of workflow_test was skipped")

def before_scenario(context, scenario):
    if "version-change" in scenario.tags:
        print("[INFO] Using submitted charts fixture")
        use_fixture(submitted_chart_test, context)
    else:
        context.test_name = scenario.name.split("@")[0][:-4].split("]")[1]
        use_fixture(workflow_test, context)
        print("made it")

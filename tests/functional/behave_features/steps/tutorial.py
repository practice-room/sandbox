from behave import *

@given('we have behave installed')
def step_impl(context):
    pass

@when('we implement a test')
def step_impl(context):
    assert True is not False

@then('behave will test it for us with {thing}!')
def step_impl(context, thing):
    print("FROM IMPLEMENTATION - thing was", thing)
    assert context.failed is False

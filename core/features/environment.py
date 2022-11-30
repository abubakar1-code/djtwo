from selenium import webdriver
import time

BEHAVE_DEBUG_ON_ERROR = True


def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")


# Before any actions take place
def before_all(context):
    setup_debug_on_error(context.config.userdata)

# Any actions that need to take place after a step
def after_step(context, step):
    # Sets up a debugger to print out a more detailed error message
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        import pdb
        pdb.post_mortem(step.exc_traceback)

    time.sleep(5)


# Any actions that need to take place before a scenario starts
def before_scenario(context, scenario):
    context.browser = webdriver.Firefox()


# Any actions that need to take place after a scenario finishes
def after_scenario(context, scenario):
    context.browser.quit()



def after_all(context):
    pass

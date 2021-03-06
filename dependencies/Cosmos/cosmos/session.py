"""
A Cosmos session.  Must be the first import of any cosmos script.
"""
import os,sys
from cosmos.config import settings

#######################
# DJANGO
#######################

#configure django settings
from cosmos import django_settings
from django.conf import settings as django_conf_settings, global_settings

#custom template context processor for web interface
django_conf_settings.configure(
    TEMPLATE_CONTEXT_PROCESSORS=global_settings.TEMPLATE_CONTEXT_PROCESSORS + ('cosmos.utils.context_processor.contproc',),
    **django_settings.__dict__)

# User can override this to specify the drmaa_native_specification method called at job submission


def default_get_drmaa_native_specification(jobAttempt):
    """
    Default method for the DRM specific resource usage flags passed in the jobtemplate's drmaa_native_specification.
    Can be overridden by the user when starting a workflow.

    :param jobAttempt: the jobAttempt being submitted
    """
    task = jobAttempt.task
    DRM = settings['DRM']

    cpu_req = task.cpu_requirement
    mem_req = task.memory_requirement
    time_req = task.time_requirement
    queue = task.workflow.default_queue

    if DRM == 'LSF':
        s = '-R "rusage[mem={0}] span[hosts=1]" -n {1}'.format(mem_req/cpu_req,cpu_req)
        if time_req:
            s += ' -W 0:{0}'.format(time_req)
        if queue:
            s += ' -q {0}'.format(queue)
        return s
    elif DRM == 'GE':
        return '-l h_vmem={mem_req}M,num_proc={cpu_req}'.format(
            mem_req=mem_req*1.5,
            cpu_req=cpu_req)
    else:
        raise Exception('DRM not supported')

#: The method to produce a :py:class:`cosmos.Job.models.JobAttempt`'s extra submission flags.
#: Can be overridden by user if special behavior is desired.
get_drmaa_native_specification = default_get_drmaa_native_specification

### print license info
warning = """
***********************************************************************************************************************
    Cosmos is currently NOT part of the public domain.  It is owned by and copywrite Harvard Medical School
    and if you do not have permission to access Cosmos then the code and its documentation are all
    off limits and you are politely instructed to stop using Cosmos immediately and delete all files related to Cosmos.

    Thank you,
    Erik Gafni
    Harvard Medical School
    erik_gafni@hms.harvard.edu
***********************************************************************************************************************
"""
printed_warning = False
if not printed_warning:
    print >> sys.stderr, warning
    printed_warning=True
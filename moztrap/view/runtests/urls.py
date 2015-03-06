"""
URLconf for running tests

"""
from django.conf.urls import patterns, url



urlpatterns = patterns(
    "moztrap.view.runtests.views",

    url(r"^$", "select", name="runtests"),
    url(r"^environment/(?P<run_id>\d+)/$",
        "set_environment",
        name="runtests_environment"),
    url(r"^run/(?P<run_id>\d+)/env/(?P<env_id>\d+)/$",
        "run",
        name="runtests_run"),

)

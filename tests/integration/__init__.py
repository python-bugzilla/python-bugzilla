import os


TEST_URL = os.getenv("BUGZILLA_URL", "http://localhost")
TEST_OWNER = "andreas@hasenkopf.xyz"
TEST_PRODUCTS = {"Red Hat Enterprise Linux 9",
                 "SUSE Linux Enterprise Server 15 SP6",
                 "TestProduct"}
TEST_SUSE_COMPONENTS = {"Containers", "Kernel"}

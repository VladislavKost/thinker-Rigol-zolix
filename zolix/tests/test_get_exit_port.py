from zolix.tests import test_common


def test():
    m = test_common.zolix_gateway.get_exit_port()
    test_common.print_result("GetExitPort", m)


if __name__ == "__main__":
    test()

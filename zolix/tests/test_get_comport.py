from zolix.tests import test_common


def test():
    m = test_common.zolix_gateway.get_comport()
    test_common.print_result("GetComport", m)


if __name__ == "__main__":
    test()

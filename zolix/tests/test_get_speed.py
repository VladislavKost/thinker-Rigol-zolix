from zolix.tests import test_common


def test():
    m = test_common.zolix_gateway.get_speed()
    test_common.print_result("GetSpeed(1)", m)


if __name__ == "__main__":
    test()

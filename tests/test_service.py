import ncs


def test_service_lifecycle(maapi):
    # CREATE
    with maapi.start_write_trans() as t:
        root = ncs.maagic.get_root(t)
        svc = root.services.l2vpn_eline.create('pytest-customer', 'pytest-l2vpn-eline-01')

        pe0 = svc.provider_edge.device.create('ios-0')
        iface0 = pe0.interface.create('GigabitEthernet2/0')
        iface0.port_mode = True

        pe1 = svc.provider_edge.device.create('ios-1')
        iface1 = pe1.interface.create('GigabitEthernet2/0')
        iface1.port_mode = True

        t.apply()

    try:
        # READ
        with maapi.start_read_trans() as t:
            root = ncs.maagic.get_root(t)
            assert ('pytest-customer', 'pytest-l2vpn-eline-01') in root.services.l2vpn_eline
            svc = root.services.l2vpn_eline['pytest-customer', 'pytest-l2vpn-eline-01']
    finally:
        # DELETE
        with maapi.start_write_trans() as t:
            root = ncs.maagic.get_root(t)
            if ('pytest-customer', 'pytest-l2vpn-eline-01') in root.services.l2vpn_eline:
                del root.services.l2vpn_eline['pytest-customer', 'pytest-l2vpn-eline-01']
                t.apply()

    # VERIFY DELETE
    with maapi.start_read_trans() as t:
        root = ncs.maagic.get_root(t)
        assert ('pytest-customer', 'pytest-l2vpn-eline-01') not in root.services.l2vpn_eline

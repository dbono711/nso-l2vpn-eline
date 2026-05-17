# -*- mode: python; python-indent: 4 -*-


from ncs.template import Template, Variables
from resource_manager.service.allocator import Allocator

from .context import ServiceContext
from .device import Device
from .network import Network


class L2vpn:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx
        self.network = Network(ctx)
        self.device = Device(ctx)

    def configure(self) -> None:
        template = Template(self.ctx.service)
        vars = Variables()
        vars.add("CUSTOMER-NAME", self.ctx.service.customer_name)
        vars.add("SERVICE-ID", self.ctx.service.service_id)

        # Allocate VPN ID from the resource manager. If the user entered a
        # VPN ID into the service model, try and allocate that one, else,
        # generate a new one
        rma = Allocator(self.ctx.service)
        vpn_id = (
            rma
            .id(request_id=self.ctx.service.vpn_id)
            .pool('primary-vpn-pool')
            .allocate(self.ctx.service.service_id)
        )
        self.ctx.service.vpn_id = vpn_id
        self.ctx.log.info(f'Allocated VPN ID {vpn_id} from the resource manager')
        vars.add("VPN-ID", vpn_id)

        devices = list(self.ctx.service.provider_edge.device)

        for i, device in enumerate(devices):
            self.ctx.log.info("Configuring device: ", device.name)
            ned_id = self.device.get_device_ned_id(device.name)
            vars.add("DEVICE-NAME", device.name)
            peer = devices[1 - i]
            peer_loopback = self.network.get_loopback_ip(peer.name, 0)
            vars.add("PEER", peer_loopback)

            for intf in device.interface:
                intf_type, intf_id = self.network.get_intf_type_and_id(device.name, intf.name)
                self.network.validate_interface(device.name, intf, intf_type, intf_id)
                vars.add("INTERFACE-NAME", intf.name)
                vars.add("INTERFACE-TYPE", intf_type)
                vars.add("INTERFACE-ID", intf_id)
                vars.add("MTU", intf.mtu)
                vars.add("PORT-MODE", intf.port_mode)
                vars.add("VLAN-ID", "")

                if "cisco-ios-cli" in ned_id:
                    cir = intf.cir * 1_000_000
                else:
                    cir = intf.cir
                vars.add("CIR", cir)

                template.apply("l2vpn-eline-template", vars)

                if not intf.port_mode:
                    for vlan_id in intf.vlan_id.as_list():
                        vars.add("VLAN-ID", vlan_id)
                        template.apply("l2vpn-eline-template", vars)

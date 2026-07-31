# Deploy OpenWrt on Proxmox VE 9

This guide imports an `x86_64` release image into a Proxmox VE 9 QEMU/KVM
virtual machine. Its default command mirrors the existing VM 202: SeaBIOS with
the i440fx machine type, a VirtIO SCSI disk, and two VirtIO network interfaces.

## Before you begin

You need:

- a Proxmox VE 9 node with shell access;
- a storage pool that supports VM disk images, such as `local-lvm`;
- one bridge for the OpenWrt LAN and one bridge for its WAN;
- an unused VM ID; and
- the `x86_64` release image and `sha256sums.txt` from this project's
  [GitHub Releases](https://github.com/IvanLi-CN/openwrt-builder/releases).

Do not connect the OpenWrt LAN interface to the PVE management bridge unless
that network is intentionally managed by OpenWrt. The image runs a DHCP server
on its LAN, so placing it on an existing managed network can cause conflicting
DHCP replies.

## Choose an image

Use `openwrt-x86-64-generic-ext4-combined.img.gz` for the configuration in this
guide. It provides a writable ext4 root filesystem and boots with SeaBIOS.

The other combined images are useful in these cases:

| Image suffix | Firmware | Root filesystem | Use case |
| --- | --- | --- | --- |
| `ext4-combined-efi.img.gz` | UEFI | ext4 | Alternative UEFI VM image |
| `squashfs-combined-efi.img.gz` | UEFI | squashfs + overlay | OpenWrt-style reset and failsafe behavior |
| `ext4-combined.img.gz` | SeaBIOS | ext4 | VM 202-compatible default |
| `squashfs-combined.img.gz` | SeaBIOS | squashfs + overlay | Legacy BIOS VM with reset support |

Do not import `generic-rootfs.tar.gz` as a VM disk. It contains a root
filesystem archive, not a bootable combined disk image.

## Prepare the PVE network

The expected interface order is:

| PVE device | OpenWrt device | Role | Suggested bridge |
| --- | --- | --- | --- |
| `net0` | `eth0` | LAN, static `192.168.31.1/24` | `vmbr0` |
| `net1` | `eth1` | WAN, DHCP client | `vmbr1` |

`vmbr0` can be an isolated bridge with no physical port for testing. Attach a
client VM to the same bridge to reach LuCI. For a physical LAN, bind the LAN
bridge to a dedicated NIC or VLAN according to the PVE host's network design.

The bridge names in the commands below are examples. Confirm the actual names
under **Node > System > Network** before creating the VM.

## Verify and unpack the image

Copy the downloaded image and `sha256sums.txt` to a directory on the PVE node,
then run:

```bash
cd /var/lib/vz/template/iso/openwrt

IMAGE_GZ=openwrt-x86-64-generic-ext4-combined.img.gz
grep "  ${IMAGE_GZ}$" sha256sums.txt | sha256sum -c -
gzip -dk "$IMAGE_GZ"
IMAGE=${IMAGE_GZ%.gz}
```

Stop if checksum verification does not report `OK`.

## Create the VM

Set the values for the PVE node, then create and configure the VM:

```bash
VMID=201
VM_NAME=OpenWRT-Lite
STORAGE=local-lvm
LAN_BRIDGE=vmbr0
WAN_BRIDGE=vmbr1
CORES=6
MEMORY_MIB=2048
CPU_TYPE=host
SCSIHW=virtio-scsi-single
EFI_DISK="${STORAGE}:0,efitype=4m,pre-enrolled-keys=1"
SCSI_DISK="${STORAGE}:0,import-from=$(pwd)/${IMAGE},iothread=1"

qm create "$VMID" \
  --name "$VM_NAME" \
  --ostype l26 \
  --bios seabios \
  --cpu "$CPU_TYPE" \
  --cores "$CORES" \
  --memory "$MEMORY_MIB" \
  --sockets 1 \
  --numa 0 \
  --scsihw "$SCSIHW" \
  --net0 "virtio,bridge=${LAN_BRIDGE}" \
  --net1 "virtio,bridge=${WAN_BRIDGE}" \
  --serial0 socket \
  --vga serial0 \
  --onboot 1 \
  --startup order=0,down=10

qm set "$VMID" --efidisk0 "$EFI_DISK"
qm set "$VMID" --scsi0 "$SCSI_DISK"

qm set "$VMID" --boot order=scsi0
qm config "$VMID"
```

The command intentionally retains VM 202's EFI disk settings even though its
default SeaBIOS boot path does not use them. The imported image already has a
1 GiB root filesystem partition, so increasing the virtual disk is optional.
Increasing only the PVE disk does not automatically expand the OpenWrt
partition or filesystem.

## First boot

Start the VM and attach to its serial console:

```bash
qm start "$VMID"
qm terminal "$VMID"
```

Press Enter when the OpenWrt console prompt appears. Log in as `root`; a new
image has no root password. Set one immediately:

```bash
passwd
ip -br address
uci show network
ifstatus wan
```

The expected defaults are:

- LuCI: `http://192.168.31.1/` from the LAN side;
- LAN: `eth0`, static `192.168.31.1/24`;
- WAN: `eth1`, DHCP client.

To leave `qm terminal`, press `Ctrl+O`.

## Optional settings

The creation command already keeps VM 202's automatic startup and shutdown
order. To change those values later:

```bash
qm set "$VMID" --onboot 1 --startup order=0,down=10
```

Back up the OpenWrt configuration before replacing or re-importing the combined
disk image. Importing a new combined image as the boot disk does not preserve
the configuration stored in the old image.

## Troubleshooting

### The VM does not boot

Confirm that the image and firmware match:

```bash
qm config "$VMID" | grep -E '^(bios|boot|scsi0|scsihw):'
```

The default `*-combined.img` image uses `bios: seabios`. If you intentionally
use an `*-combined-efi.img` image instead, configure OVMF and an EFI disk:

```bash
qm set "$VMID" --bios ovmf
qm set "$VMID" --efidisk0 "${STORAGE}:0,efitype=4m,pre-enrolled-keys=0"
```

### LuCI is unreachable

Check that `net0` is attached to the LAN bridge and that the client is on the
same bridge or routed network. From the OpenWrt console, confirm the address and
web service:

```bash
ip -br address show br-lan
/etc/init.d/uhttpd status
```

### The WAN has no address

Check the second NIC and DHCP status:

```bash
ip link show eth1
ifstatus wan
logread -e netifd -e udhcpc
```

Confirm that PVE `net1` is connected to a bridge with upstream DHCP access. If
the interfaces were intentionally attached in the opposite order, correct the
PVE bridge assignments or update the OpenWrt network configuration from the
serial console.

## References

- [Proxmox VE 9 QEMU/KVM Virtual Machines](https://pve.proxmox.com/pve-docs/chapter-qm.html)
- [Proxmox VE 9 `qm` manual](https://pve.proxmox.com/pve-docs/qm.1.html)
- [OpenWrt on x86 hardware](https://openwrt.org/docs/guide-user/installation/openwrt_x86)

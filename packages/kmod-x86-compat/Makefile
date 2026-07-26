# SPDX-License-Identifier: GPL-2.0-only
#
# Package official Linux 6.12 modules that OpenWrt 25.12 does not expose for x86_64.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

define KernelPackage/wangxun-libwx
  SUBMENU:=$(NETWORK_DEVICES_MENU)
  TITLE:=Wangxun Ethernet shared library
  DEPENDS:=@PCI_SUPPORT
  KCONFIG:=CONFIG_LIBWX
  FILES:=$(LINUX_DIR)/drivers/net/ethernet/wangxun/libwx/libwx.ko
  AUTOLOAD:=$(call AutoProbe,libwx)
endef

define KernelPackage/wangxun-libwx/description
 Shared library required by the official Wangxun NGBE and TXGBE drivers.
endef

$(eval $(call KernelPackage,wangxun-libwx))

define KernelPackage/ngbe
  SUBMENU:=$(NETWORK_DEVICES_MENU)
  TITLE:=Wangxun GbE PCI Express adapters
  DEPENDS:=@PCI_SUPPORT +kmod-phylink +kmod-wangxun-libwx
  KCONFIG:=CONFIG_NGBE
  FILES:=$(LINUX_DIR)/drivers/net/ethernet/wangxun/ngbe/ngbe.ko
  AUTOLOAD:=$(call AutoProbe,ngbe)
endef

define KernelPackage/ngbe/description
 Official Linux driver for Wangxun GbE PCI Express adapters.
endef

$(eval $(call KernelPackage,ngbe))

define KernelPackage/txgbe
  SUBMENU:=$(NETWORK_DEVICES_MENU)
  TITLE:=Wangxun 10GbE PCI Express adapters
  DEPENDS:=@PCI_SUPPORT +kmod-i2c-designware-platform +kmod-pcs-xpcs +kmod-phylink +kmod-sfp +kmod-wangxun-libwx
  KCONFIG:=CONFIG_TXGBE
  FILES:=$(LINUX_DIR)/drivers/net/ethernet/wangxun/txgbe/txgbe.ko
  AUTOLOAD:=$(call AutoProbe,txgbe)
endef

define KernelPackage/txgbe/description
 Official Linux driver for Wangxun 10GbE PCI Express adapters.
endef

$(eval $(call KernelPackage,txgbe))

define KernelPackage/sound-hda-intel-x86-64
  SUBMENU:=$(SOUND_MENU)
  TITLE:=HD Audio Intel driver for x86_64
  DEPENDS:=@TARGET_x86_64 +kmod-sound-hda-core
  KCONFIG:= \
    CONFIG_SOUND_PCI \
    CONFIG_SND_HDA_INTEL
  FILES:= \
    $(LINUX_DIR)/sound/pci/hda/snd-hda-intel.ko \
    $(LINUX_DIR)/sound/hda/snd-intel-dspcfg.ko
  AUTOLOAD:=$(call AutoProbe,snd-hda-intel)
endef

define KernelPackage/sound-hda-intel-x86-64/description
 Official Linux Intel HD Audio driver, exposed for the x86_64 target.
endef

$(eval $(call KernelPackage,sound-hda-intel-x86-64))

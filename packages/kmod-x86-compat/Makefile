# SPDX-License-Identifier: GPL-2.0-only
#
# Package official Linux 6.12 modules that OpenWrt 25.12 does not expose for x86_64.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk
include $(INCLUDE_DIR)/package.mk

define KernelPackage/wangxun-libwx
  SUBMENU:=Network Devices
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
  SUBMENU:=Network Devices
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
  SUBMENU:=Network Devices
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

define KernelPackage/sound-core-x86-64
  SUBMENU:=Sound
  TITLE:=Sound support for x86_64
  DEPENDS:=@PCI_SUPPORT +kmod-input-core
  KCONFIG:= \
    CONFIG_SOUND \
    CONFIG_SND \
    CONFIG_SND_HWDEP \
    CONFIG_SND_RAWMIDI \
    CONFIG_SND_TIMER \
    CONFIG_SND_PCM \
    CONFIG_SND_PCM_TIMER=y \
    CONFIG_SND_SEQUENCER \
    CONFIG_SND_VIRMIDI \
    CONFIG_SND_SEQ_DUMMY \
    CONFIG_SND_SEQUENCER_OSS=y \
    CONFIG_HOSTAUDIO \
    CONFIG_SND_PCM_OSS \
    CONFIG_SND_MIXER_OSS \
    CONFIG_SOUND_OSS_CORE_PRECLAIM=y \
    CONFIG_SND_COMPRESS_OFFLOAD
  FILES:= \
    $(LINUX_DIR)/sound/soundcore.ko \
    $(LINUX_DIR)/sound/core/snd.ko \
    $(LINUX_DIR)/sound/core/snd-hwdep.ko \
    $(LINUX_DIR)/sound/core/snd-seq-device.ko \
    $(LINUX_DIR)/sound/core/snd-rawmidi.ko \
    $(LINUX_DIR)/sound/core/snd-timer.ko \
    $(LINUX_DIR)/sound/core/snd-pcm.ko \
    $(LINUX_DIR)/sound/core/oss/snd-mixer-oss.ko \
    $(LINUX_DIR)/sound/core/oss/snd-pcm-oss.ko \
    $(LINUX_DIR)/sound/core/snd-compress.ko
  AUTOLOAD:=$(call AutoLoad,30,soundcore snd snd-hwdep snd-seq-device snd-rawmidi snd-timer snd-pcm snd-mixer-oss snd-pcm-oss snd-compress)
endef

define KernelPackage/sound-core-x86-64/description
 Official Linux sound core, exposed for the x86_64 target.
endef

$(eval $(call KernelPackage,sound-core-x86-64))

define KernelPackage/sound-hda-core-x86-64
  SUBMENU:=Sound
  TITLE:=HD Audio sound core for x86_64
  DEPENDS:=@PCI_SUPPORT +kmod-regmap-core +kmod-sound-core-x86-64
  KCONFIG:= \
    CONFIG_SND_HDA_CORE \
    CONFIG_SND_HDA_HWDEP=y \
    CONFIG_SND_HDA_RECONFIG=n \
    CONFIG_SND_HDA_INPUT_BEEP=n \
    CONFIG_SND_HDA_PATCH_LOADER=n \
    CONFIG_SND_HDA_GENERIC
  FILES:= \
    $(LINUX_DIR)/sound/hda/snd-hda-core.ko \
    $(LINUX_DIR)/sound/pci/hda/snd-hda-codec.ko \
    $(LINUX_DIR)/sound/pci/hda/snd-hda-codec-generic.ko
  AUTOLOAD:=$(call AutoProbe,snd-hda-core snd-hda-codec snd-hda-codec-generic)
endef

define KernelPackage/sound-hda-core-x86-64/description
 Official Linux HD Audio sound core, exposed for the x86_64 target.
endef

$(eval $(call KernelPackage,sound-hda-core-x86-64))

define KernelPackage/sound-hda-intel-x86-64
  SUBMENU:=Sound
  TITLE:=HD Audio Intel driver for x86_64
  DEPENDS:=@PCI_SUPPORT +kmod-sound-hda-core-x86-64
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

define KernelPackage/sound-hda-codec-realtek-x86-64
  SUBMENU:=Sound
  TITLE:=HD Audio Realtek codec for x86_64
  DEPENDS:=@PCI_SUPPORT +kmod-sound-hda-core-x86-64
  KCONFIG:= \
    CONFIG_SND_HDA_SCODEC_COMPONENT \
    CONFIG_SND_HDA_CODEC_REALTEK
  FILES:= \
    $(LINUX_DIR)/sound/pci/hda/snd-hda-scodec-component.ko \
    $(LINUX_DIR)/sound/pci/hda/snd-hda-codec-realtek.ko
  AUTOLOAD:=$(call AutoProbe,snd-hda-scodec-component snd-hda-codec-realtek)
endef

define KernelPackage/sound-hda-codec-realtek-x86-64/description
 Official Linux Realtek HD Audio codec, exposed for the x86_64 target.
endef

$(eval $(call KernelPackage,sound-hda-codec-realtek-x86-64))

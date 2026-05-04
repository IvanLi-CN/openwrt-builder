include $(TOPDIR)/rules.mk

PKG_NAME:=luci-app-zerotier
PKG_VERSION:=1.0
PKG_RELEASE:=1

LUCI_TITLE:=LuCI support for ZeroTier
LUCI_DEPENDS:=+luci-base +zerotier
LUCI_PKGARCH:=all

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature

{pkgs}: {
  deps = [
    pkgs.eudev
    pkgs.mesa
    pkgs.xorg.libX11
    pkgs.dbus
    pkgs.libxkbcommon
    pkgs.xorg.libXfixes
    pkgs.xorg.libxcb
    pkgs.xorg.libXrandr
    pkgs.xorg.libXext
    pkgs.xorg.libXdamage
    pkgs.xorg.libXcomposite
    pkgs.alsa-lib
    pkgs.cairo
    pkgs.pango
    pkgs.expat
    pkgs.libdrm
    pkgs.cups
    pkgs.atk
    pkgs.nspr
    pkgs.nss
    pkgs.glib
  ];
}
